from xml.dom.minidom import Element
from pvm.xml import get_ref

def get_associated_data(ref:str, data:dict) -> dict:
    ''' given a reference returns its asociated data in the data dictionary '''
    if 'form-array' not in data:
        return {}

    for form in data['form_array']:
        if type(form) != dict:
            continue

        if 'ref' not in form:
            continue

        if form['ref'] == ref:
            return form['ref']

    return {}

def validate_input(input:Element, value):
    ''' Validates the given value against the requirements specified by the
    input element '''
    if input.getAttribute('type') == 'text':
        if input.getAttribute('required') and not value:
            raise InputValidationError('required')

def validate_form(form:Element, data:dict) -> dict:
    ''' Validates the given data against the spec contained in form. In case of
    failure raises an exception. In case of success returns the validated data.
    '''
    ref = get_ref(form)

    given_data = get_associated_data(ref, data)
    collected_data = {}

    for input in form.getElementsByTagName('input'):
        name = input.getAttribute('name')

        try:
            collected_data[name] = validate_input(input, given_data.get(name))
        except InputValidationError as e:
            errors.append(e)

    if errors:
        raise ValidationErrors(errors)

    return collected_data
