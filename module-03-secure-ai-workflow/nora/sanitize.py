"""Output boundary: detect and redact sensitive data with Microsoft Presidio."""
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

ENTITIES = ["IBAN_CODE", "CREDIT_CARD", "EMAIL_ADDRESS", "PHONE_NUMBER"]
# Public data that must NOT be redacted (avoids over-redaction / false positives)
ALLOW_LIST = ["+39 049 000 0000"]

nlp = NlpEngineProvider(nlp_configuration={
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
}).create_engine()
analyzer = AnalyzerEngine(nlp_engine=nlp)
anonymizer = AnonymizerEngine()


def redact(text: str) -> tuple[str, list[str]]:
    """Return the text with sensitive entities replaced by <ENTITY_TYPE>, plus what was found."""
    findings = analyzer.analyze(text=text, language="en", entities=ENTITIES, allow_list=ALLOW_LIST)
    redacted = anonymizer.anonymize(text=text, analyzer_results=findings).text
    return redacted, sorted({f.entity_type for f in findings})
