import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _doctype_template_map():
    source = (ROOT / "emails/email_service/generic_email.py").read_text()
    module = ast.parse(source)
    for node in module.body:
        if isinstance(node, ast.Assign):
            if any(getattr(target, "id", None) == "DOCTYPE_TEMPLATE_MAP" for target in node.targets):
                return ast.literal_eval(node.value)
    raise AssertionError("DOCTYPE_TEMPLATE_MAP not found")


def _supported_button_doctypes():
    source = (ROOT / "emails/public/js/send_email_button.js").read_text()
    match = re.search(r"emails\.SUPPORTED_DOCTYPES\s*=\s*\[(.*?)\];", source, re.S)
    assert match, "emails.SUPPORTED_DOCTYPES not found"
    return re.findall(r'"([^"]+)"', match.group(1))


def test_home_build_request_is_not_email_button_supported():
    assert "Home Build Request" not in _supported_button_doctypes()


def test_home_build_request_has_no_default_document_template():
    assert "Home Build Request" not in _doctype_template_map()


def test_dcr_workflow_doctypes_are_not_generic_email_button_supported():
    workflow_doctypes = {"Customer", "Loan Application", "Loan", "Loan Disbursement"}

    assert workflow_doctypes.isdisjoint(_supported_button_doctypes())


def test_dcr_workflow_doctypes_have_no_default_document_template():
    workflow_doctypes = {"Customer", "Loan Application", "Loan", "Loan Disbursement"}

    assert workflow_doctypes.isdisjoint(_doctype_template_map())


def test_button_supported_doctypes_do_not_use_generic_document_template():
    template_map = _doctype_template_map()

    for doctype in _supported_button_doctypes():
        assert template_map.get(doctype) != "document"


def test_unsupported_doctypes_do_not_fall_back_to_generic_document_template():
    source = (ROOT / "emails/email_service/generic_email.py").read_text()
    assert 'DOCTYPE_TEMPLATE_MAP.get(doctype, "document")' not in source
