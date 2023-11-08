from src.case_wizard import CaseWizard
from src.enum_hatchery import StringCase


# =========================================================================== #

def test_to_camel_case():
    wizard = CaseWizard("hello world", StringCase.CAMEL)
    assert wizard.convert() == "helloWorld"

def test_to_cobol_case():
    wizard = CaseWizard("hello world", StringCase.COBOL)
    assert wizard.convert() == "HELLO-WORLD"

def test_to_kebab_case():
    wizard = CaseWizard("hello world", StringCase.KEBAB)
    assert wizard.convert() == "hello-world"

def test_to_pascal_case():
    wizard = CaseWizard("hello world", StringCase.PASCAL)
    assert wizard.convert() == "HelloWorld"

def test_to_scream_case():
    wizard = CaseWizard("hello world", StringCase.SCREAM)
    assert wizard.convert() == "HELLO_WORLD"

def test_to_snake_case():
    wizard = CaseWizard("hello world", StringCase.SNAKE)
    assert wizard.convert() == "hello_world"

def test_to_lower_case():
    wizard = CaseWizard("HeLLo WoRLd", StringCase.LOWER)
    assert wizard.convert() == "hello world"

def test_to_upper_case():
    wizard = CaseWizard("HeLLo WoRLd", StringCase.UPPER)
    assert wizard.convert() == "HELLO WORLD"

def test_to_title_case():
    wizard = CaseWizard("hello world", StringCase.TITLE)
    assert wizard.convert() == "Hello World"

def test_to_spongebob_case():
    wizard = CaseWizard("hello world", StringCase.SPONGEBOB)
    assert wizard.convert() == "HeLLo WoRLd"

def test_empty_string():
    wizard = CaseWizard("", StringCase.CAMEL)
    assert wizard.convert() == ""

def test_whitespace_string():
    wizard = CaseWizard("    ", StringCase.SNAKE)
    assert wizard.convert() == "____"
