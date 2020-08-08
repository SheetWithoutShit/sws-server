"""This module provides validators for models data."""

import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.]+@[a-zA-Z0-9_.]{2,}\.[a-zA-Z0-9_.]+$")


def validate_email(email):
    """
    Validate user email value.
    * Consist of case-insensitive alphanumeric characters.
    * Periods or underscores are allowed.
    * Contains no white spaces.
    * Account has at least one character.
    * Domain has at least two characters.
    * Contains @ symbol between account and domain.
    """
    errors = []
    if not isinstance(email, str):
        errors.append("Email must be string type.")
        return errors

    if not EMAIL_REGEX.match(email):
        errors.append("Email must have correct format (example@mail.com).")

    return errors


def validate_password(password):
    """Validate user password value."""
    errors = []
    if not isinstance(password, str):
        errors.append("Password must be string type.")
        return errors

    if len(password) < 8:
        errors.append("Password must have minimum 8 characters.")
    password_chars = set(password)
    if not any(c.islower() for c in password_chars):
        errors.append("Password must have at least one lowercase letter.")
    if not any(c.isupper() for c in password_chars):
        errors.append("Password must have at least one uppercase letter.")
    if not any(c.isdigit() for c in password_chars):
        errors.append("Password must have at least one digit.")

    return errors


def validate_budget_income(income):
    """Validate budget income value."""
    errors = []
    if not isinstance(income, float):
        errors.append("Income must be float type.")
        return errors

    if income < 0:
        errors.append("Income must be positive value.")

    return errors


def validate_budget_savings(savings):
    """Validate budget savings input."""
    errors = []
    if not isinstance(savings, int):
        errors.append("Savings must be integer type.")
        return errors

    if not 0 <= savings <= 100:
        errors.append("Savings is out of range (0-100).")

    return errors
