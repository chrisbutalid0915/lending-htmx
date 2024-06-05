from numpy_financial import pmt
from decimal import Decimal, ROUND_HALF_UP


def merge_terms(terms, interest_rate, status):
    merged_list = []

    for terms, interest_rate, status in zip(terms, interest_rate, status):
        merged_list.append(
            {
                "terms": int(terms),
                "interest_rate": float(interest_rate),
                "status": str(
                    status.capitalize()
                ),  # Convert 'true' to True, 'false' to False
            }
        )
    return merged_list


def calculate_loan_payment(interest_rate, terms, loan_amount) -> Decimal:
    interest_rate = interest_rate / terms
    if interest_rate == 0:
        monthly_payment = -loan_amount / terms
    else:
        monthly_payment = pmt(interest_rate, terms, -loan_amount)

    return Decimal(monthly_payment).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)


def calculate_loan_interest(interest_rate, terms, loan_amount):
    monthly_payment = calculate_loan_payment(
        interest_rate, terms, loan_amount
    )  # compute the monthly payment
    monthly_interest_rate = interest_rate / terms  # get monthly interest

    balance = loan_amount  # set running balance
    interest_amount = 0
    for _ in range(terms):
        interest = balance * monthly_interest_rate  # get the monthly interest
        principal_amount = monthly_payment - interest  # get the principal amount
        balance -= principal_amount  # compute the running balance
        interest_amount += interest

    return interest_amount


def calculate_payment_interest_and_principal(
    loan_amount, terms, interest_rate, remaining_balance
):
    monthly_interest_rate = interest_rate / terms
    interest_amount = remaining_balance * monthly_interest_rate
    monthly_payment = calculate_loan_payment(
        interest_rate=interest_rate, terms=terms, loan_amount=loan_amount
    )  # compute the monthly payment
    principal_amount = monthly_payment - interest_amount
    return interest_amount, principal_amount
