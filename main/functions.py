def generate_form_errors(form):
    message = ""
    for field, errors in form.errors.items():  # Iterate over all field errors
        for error in errors:
            message += f"{error} "  # Append each error message

    for err in form.non_field_errors():  # Handle non-field errors
        message += f"{err} "
    
    return message.strip()  # Remove extra spaces




