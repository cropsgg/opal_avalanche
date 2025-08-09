from __future__ import annotations

import re
from typing import Dict, List, Tuple, Any, Optional
import structlog
from datetime import datetime

log = structlog.get_logger()


class PIIRedactor:
    """
    PII detection and redaction system for Indian legal documents
    Supports pattern-based and NER-based detection
    """
    
    def __init__(self):
        # Indian-specific PII patterns with high precision
        self.patterns = {
            "aadhaar": {
                "regex": r'\b\d{4}\s*\d{4}\s*\d{4}\b',
                "confidence": 0.95,
                "description": "Aadhaar number (12 digits)"
            },
            "pan": {
                "regex": r'\b[A-Z]{5}\d{4}[A-Z]\b',
                "confidence": 0.98,
                "description": "PAN number"
            },
            "phone_indian": {
                "regex": r'(\+91\s*)?[6-9]\d{9}\b',
                "confidence": 0.90,
                "description": "Indian mobile number"
            },
            "phone_landline": {
                "regex": r'\b\d{2,4}-\d{6,8}\b',
                "confidence": 0.75,
                "description": "Landline number"
            },
            "email": {
                "regex": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                "confidence": 0.95,
                "description": "Email address"
            },
            "bank_account": {
                "regex": r'\b\d{9,20}\b',
                "confidence": 0.60,  # Lower confidence as could be other numbers
                "description": "Bank account number"
            },
            "ifsc": {
                "regex": r'\b[A-Z]{4}0[A-Z0-9]{6}\b',
                "confidence": 0.95,
                "description": "IFSC code"
            },
            "driving_license": {
                "regex": r'\b[A-Z]{2}\d{2}\s?\d{11}\b',
                "confidence": 0.85,
                "description": "Driving license number"
            },
            "voter_id": {
                "regex": r'\b[A-Z]{3}\d{7}\b',
                "confidence": 0.80,
                "description": "Voter ID number"
            },
            "passport": {
                "regex": r'\b[A-Z]\d{7}\b',
                "confidence": 0.85,
                "description": "Passport number"
            },
            "gst": {
                "regex": r'\b\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z0-9]\b',
                "confidence": 0.95,
                "description": "GST number"
            },
            "pin_code": {
                "regex": r'\b\d{6}\b',
                "confidence": 0.50,  # Low confidence as could be other 6-digit numbers
                "description": "PIN code"
            }
        }
        
        # Common name patterns (for basic name detection without spaCy)
        self.name_patterns = {
            "honorifics": r'\b(Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Prof\.?|Shri|Smt\.?|Kumari)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            "full_names": r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b',
            "indian_names": r'\b(Ram|Krishna|Sharma|Singh|Kumar|Devi|Prasad|Lal|Das|Gupta|Agarwal|Jain|Shah|Patel)\b'
        }
        
        # Initialize spaCy model if available
        self.nlp = None
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
            log.info("pii_redactor.spacy_loaded")
        except (ImportError, OSError):
            log.warning("pii_redactor.spacy_unavailable", 
                       msg="spaCy not available, using pattern-based detection only")
    
    def detect_and_redact_pii(self, text: str, user_id: Optional[str] = None, 
                             redaction_mode: str = "mask") -> Dict[str, Any]:
        """
        Main method to detect and redact PII from text
        
        Args:
            text: Input text to process
            user_id: User ID for audit logging
            redaction_mode: 'mask', 'remove', or 'placeholder'
        
        Returns:
            Dict with original text, redacted text, and detection metadata
        """
        log.info("pii_redactor.start", 
                text_length=len(text), 
                user_id=user_id,
                redaction_mode=redaction_mode)
        
        detected_pii = []
        redacted_text = text
        
        # Pattern-based detection
        pattern_detections = self._detect_patterns(text)
        detected_pii.extend(pattern_detections)
        
        # NER-based detection (if spaCy available)
        if self.nlp:
            ner_detections = self._detect_with_ner(text)
            detected_pii.extend(ner_detections)
        else:
            # Fallback name detection
            name_detections = self._detect_names_basic(text)
            detected_pii.extend(name_detections)
        
        # Sort by position (reverse order for easier replacement)
        detected_pii.sort(key=lambda x: x['start'], reverse=True)
        
        # Remove overlapping detections (keep higher confidence)
        filtered_pii = self._remove_overlaps(detected_pii)
        
        # Apply redaction
        redacted_text = self._apply_redaction(text, filtered_pii, redaction_mode)
        
        # Generate summary
        pii_summary = self._generate_summary(filtered_pii)
        
        result = {
            "original_text": text,
            "redacted_text": redacted_text,
            "pii_detected": filtered_pii,
            "summary": pii_summary,
            "redaction_mode": redaction_mode,
            "processed_at": datetime.utcnow().isoformat(),
            "has_pii": len(filtered_pii) > 0
        }
        
        log.info("pii_redactor.complete", 
                pii_count=len(filtered_pii),
                has_pii=result["has_pii"],
                text_length_change=len(text) - len(redacted_text))
        
        return result
    
    def _detect_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII using regex patterns"""
        detections = []
        
        for pii_type, pattern_info in self.patterns.items():
            pattern = pattern_info["regex"]
            confidence = pattern_info["confidence"]
            description = pattern_info["description"]
            
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            
            for match in matches:
                # Additional validation for some patterns
                if self._validate_detection(pii_type, match.group(), text, match.start()):
                    detections.append({
                        "type": pii_type,
                        "value": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": confidence,
                        "method": "pattern",
                        "description": description
                    })
        
        return detections
    
    def _detect_with_ner(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII using spaCy NER"""
        if not self.nlp:
            return []
        
        detections = []
        doc = self.nlp(text)
        
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE", "LOC"]:
                # Filter out common legal terms that aren't actually PII
                if not self._is_legal_term(ent.text):
                    confidence = 0.8 if ent.label_ == "PERSON" else 0.6
                    
                    detections.append({
                        "type": f"ner_{ent.label_.lower()}",
                        "value": ent.text,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": confidence,
                        "method": "ner",
                        "description": f"Named entity: {ent.label_}"
                    })
        
        return detections
    
    def _detect_names_basic(self, text: str) -> List[Dict[str, Any]]:
        """Basic name detection without spaCy"""
        detections = []
        
        for pattern_name, pattern in self.name_patterns.items():
            matches = list(re.finditer(pattern, text))
            
            for match in matches:
                name = match.group()
                # Skip common legal terms
                if not self._is_legal_term(name):
                    confidence = 0.7 if "honorifics" in pattern_name else 0.5
                    
                    detections.append({
                        "type": "name",
                        "value": name,
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": confidence,
                        "method": "pattern_names",
                        "description": f"Potential name ({pattern_name})"
                    })
        
        return detections
    
    def _validate_detection(self, pii_type: str, value: str, text: str, position: int) -> bool:
        """Additional validation for certain PII types"""
        
        if pii_type == "bank_account":
            # Bank account numbers should be in financial context
            context = text[max(0, position-50):position+50].lower()
            financial_keywords = ["account", "bank", "deposit", "withdrawal", "balance", "ifsc"]
            if not any(keyword in context for keyword in financial_keywords):
                return False
        
        elif pii_type == "pin_code":
            # PIN codes should be in address context
            context = text[max(0, position-50):position+50].lower()
            address_keywords = ["pin", "postal", "address", "city", "state", "district"]
            if not any(keyword in context for keyword in address_keywords):
                return False
        
        elif pii_type == "phone_indian":
            # Validate Indian mobile number format
            digits_only = re.sub(r'\D', '', value)
            if len(digits_only) == 10 and digits_only[0] in '6789':
                return True
            elif len(digits_only) == 12 and digits_only.startswith('91') and digits_only[2] in '6789':
                return True
            return False
        
        return True
    
    def _is_legal_term(self, text: str) -> bool:
        """Check if text is a common legal term rather than PII"""
        legal_terms = {
            "plaintiff", "defendant", "appellant", "respondent", "petitioner",
            "court", "judge", "magistrate", "tribunal", "commission",
            "section", "article", "act", "rule", "regulation", "order",
            "supreme court", "high court", "district court", "civil court",
            "criminal court", "session court", "family court", "india",
            "indian", "delhi", "mumbai", "bangalore", "chennai", "kolkata",
            "government", "state", "central", "ministry", "department",
            "advocate", "counsel", "lawyer", "attorney", "solicitor"
        }
        
        return text.lower() in legal_terms
    
    def _remove_overlaps(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove overlapping detections, keeping higher confidence ones"""
        if not detections:
            return []
        
        # Sort by start position
        sorted_detections = sorted(detections, key=lambda x: x['start'])
        filtered = []
        
        for detection in sorted_detections:
            # Check for overlap with previously added detections
            overlap = False
            for existing in filtered:
                if (detection['start'] < existing['end'] and 
                    detection['end'] > existing['start']):
                    # Overlapping - keep the one with higher confidence
                    if detection['confidence'] > existing['confidence']:
                        filtered.remove(existing)
                        filtered.append(detection)
                    overlap = True
                    break
            
            if not overlap:
                filtered.append(detection)
        
        return filtered
    
    def _apply_redaction(self, text: str, detections: List[Dict[str, Any]], 
                        mode: str) -> str:
        """Apply redaction to text based on detections"""
        if not detections:
            return text
        
        # Sort by position (reverse for easier replacement)
        sorted_detections = sorted(detections, key=lambda x: x['start'], reverse=True)
        redacted = text
        
        for detection in sorted_detections:
            start, end = detection['start'], detection['end']
            pii_type = detection['type']
            original_value = detection['value']
            
            if mode == "mask":
                # Replace with masked version
                if pii_type in ["aadhaar", "pan", "phone_indian", "phone_landline"]:
                    replacement = self._mask_sensitive(original_value)
                else:
                    replacement = f"[{pii_type.upper()}_REDACTED]"
            
            elif mode == "remove":
                # Remove entirely
                replacement = ""
            
            elif mode == "placeholder":
                # Replace with descriptive placeholder
                replacement = f"[{detection.get('description', pii_type).upper()}]"
            
            else:
                # Default: placeholder mode
                replacement = f"[{pii_type.upper()}_REDACTED]"
            
            redacted = redacted[:start] + replacement + redacted[end:]
        
        return redacted
    
    def _mask_sensitive(self, value: str) -> str:
        """Create masked version of sensitive data"""
        if len(value) <= 4:
            return "X" * len(value)
        
        # Show first 2 and last 2 characters, mask the middle
        visible_chars = 2
        if len(value) > 10:
            visible_chars = 3
        
        return (value[:visible_chars] + 
                "X" * (len(value) - 2 * visible_chars) + 
                value[-visible_chars:])
    
    def _generate_summary(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of PII detection results"""
        if not detections:
            return {"total_pii": 0, "types_detected": [], "high_confidence_count": 0}
        
        types_count = {}
        high_confidence_count = 0
        
        for detection in detections:
            pii_type = detection['type']
            confidence = detection['confidence']
            
            types_count[pii_type] = types_count.get(pii_type, 0) + 1
            
            if confidence >= 0.8:
                high_confidence_count += 1
        
        return {
            "total_pii": len(detections),
            "types_detected": list(types_count.keys()),
            "types_count": types_count,
            "high_confidence_count": high_confidence_count,
            "average_confidence": sum(d['confidence'] for d in detections) / len(detections)
        }
    
    def redact_for_agents(self, text: str, user_id: str) -> str:
        """
        Redact PII for agent processing
        Returns redacted text suitable for LLM processing
        """
        result = self.detect_and_redact_pii(text, user_id, redaction_mode="placeholder")
        return result["redacted_text"]
    
    def audit_pii_detection(self, text: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Detect PII for audit purposes without redaction
        Returns detailed detection results for compliance logging
        """
        result = self.detect_and_redact_pii(text, user_id, redaction_mode="mask")
        return result["pii_detected"]


# Global redactor instance
_redactor_instance: Optional[PIIRedactor] = None


def get_pii_redactor() -> PIIRedactor:
    """Get global PII redactor instance (singleton)"""
    global _redactor_instance
    if _redactor_instance is None:
        _redactor_instance = PIIRedactor()
    return _redactor_instance


def redact_user_input(text: str, user_id: str, mode: str = "placeholder") -> Dict[str, Any]:
    """
    Main function to redact PII from user input
    """
    return get_pii_redactor().detect_and_redact_pii(text, user_id, mode)


def redact_for_processing(text: str, user_id: str) -> str:
    """
    Redact PII for agent/LLM processing
    Returns clean text safe for AI processing
    """
    return get_pii_redactor().redact_for_agents(text, user_id)


if __name__ == "__main__":
    # Test the PII redaction system
    test_cases = [
        "My name is Ram Kumar and my phone number is 9876543210. My Aadhaar is 1234 5678 9012 and PAN is ABCDE1234F.",
        "Contact me at ram.kumar@email.com or call +91 9876543210.",
        "Bank account 123456789012345 with IFSC HDFC0001234.",
        "Please file a case in the Supreme Court of India regarding Section 302 IPC.",
        "The Hon'ble Judge delivered the judgment in Civil Appeal No. 123/2023."
    ]
    
    redactor = PIIRedactor()
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n=== Test Case {i} ===")
        print(f"Original: {test_text}")
        
        result = redactor.detect_and_redact_pii(test_text, "test_user")
        print(f"Redacted: {result['redacted_text']}")
        print(f"PII Found: {len(result['pii_detected'])}")
        
        for pii in result['pii_detected']:
            print(f"  - {pii['type']}: {pii['value']} (confidence: {pii['confidence']:.2f})")
