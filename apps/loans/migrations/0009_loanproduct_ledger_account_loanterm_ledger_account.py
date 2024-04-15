# Generated by Django 4.2.4 on 2024-04-04 02:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("ledger_accounts", "0001_initial"),
        ("loans", "0008_alter_payment_payment_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="loanproduct",
            name="ledger_account",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ledger_accounts.ledgeraccount",
            ),
        ),
        migrations.AddField(
            model_name="loanterm",
            name="ledger_account",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ledger_accounts.ledgeraccount",
            ),
        ),
    ]