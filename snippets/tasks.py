from django.core.mail import send_mail

from django_snippets.settings import EMAIL_HOST_USER as sender

# Send an email notification to the user when a snippet is created.
# The email contains the snippet's name and description.
# TODO: Implement email sending logic and integrate with Celery
def sendEmailInSnippetCreation(snippet_name, snippet_description, user_mail):
    # subject = 'Snippet "' + snippet_name + '" created successfully'
    # body = (
    #     'The snippet "' + snippet_name + '" was created with the following description: \n'
    #     + snippet_description
    # )

    # Only send the email if the user has registered an email address
    if user_mail:
        # TODO: Fill in the email sending logic
        # Placeholder: send_mail(subject, body, sender, [])
        pass
