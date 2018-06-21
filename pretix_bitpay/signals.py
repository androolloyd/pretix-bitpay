import json
from collections import OrderedDict

from django import forms
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _

from pretix.base.shredder import BaseDataShredder
from pretix.base.signals import (
    logentry_display, register_global_settings,
    register_payment_providers, requiredaction_display,
    register_data_shredders)


@receiver(register_payment_providers, dispatch_uid="payment_bitpay")
def register_payment_provider(sender, **kwargs):
    from .payment import BitPay
    return BitPay


@receiver(signal=logentry_display, dispatch_uid="bitpay_logentry_display")
def pretixcontrol_logentry_display(sender, logentry, **kwargs):
    if logentry.action_type != 'pretix_bitpay.event':
        return

    data = json.loads(logentry.data)
    event_type = data.get('type')
    return _('BitPay reported an event: {}').format(event_type)


@receiver(signal=requiredaction_display, dispatch_uid="bitpay_requiredaction_display")
def pretixcontrol_action_display(sender, action, request, **kwargs):
    if not action.action_type.startswith('pretix_bitpay'):
        return

    data = json.loads(action.data)

    if action.action_type == 'pretix_bitpay.refund':
        template = get_template('pretix_bitpay/action_refund.html')
    elif action.action_type == 'pretix_bitpay.overpaid':
        template = get_template('pretix_bitpay/action_overpaid.html')

    ctx = {'data': data, 'event': sender, 'action': action}
    return template.render(ctx, request)


@receiver(register_global_settings, dispatch_uid='bitpay_global_settings')
def register_global_settings(sender, **kwargs):
    return OrderedDict([
        ('payment_bitpay_pem', forms.CharField(
            label=_('BitPay client: Private Key'),
            required=False,
            widget=forms.Textarea
        )),
    ])


class PaymentLogsShredder(BaseDataShredder):
    verbose_name = _('BitPay payment history')
    identifier = 'bitpay_logs'
    description = _('This will remove payment-related history information. No download will be offered.')

    def generate_files(self):
        pass

    def shred_data(self):
        for le in self.event.logentry_set.filter(action_type="pretix_bitpay.event").exclude(data=""):
            d = le.parsed_data
            if 'data' in d:
                for k, v in list(d['data'].items()):
                    if v not in ('id', 'status', 'price', 'currency', 'invoiceTime', 'paymentSubtotals',
                                 'paymentTotals', 'transactionCurrency', 'amountPaid'):
                        d['data'][k] = '█'
                le.data = json.dumps(d)
                le.shredded = True
                le.save(update_fields=['data', 'shredded'])


@receiver(register_data_shredders, dispatch_uid="bitpay_shredders")
def register_shredder(sender, **kwargs):
    return [
        PaymentLogsShredder,
    ]