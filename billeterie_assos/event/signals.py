from django.db.models.signals import post_save, post_init, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from event.models import Profile, Event, Boss, Price
from django.core.mail import send_mail, EmailMessage
from django.urls import reverse
import absoluteuri


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

"""
@receiver(post_save, sender=Event)  # maybe cleaner to create email object and modify it with if then send it
def send_email_event_post(sender, instance, created, **kwargs):
    to_boss = EmailMessage(
                'Validate an event',
                'This event needs validation.\n%s' % absoluteuri.build_absolute_uri(reverse(
                        'event:event_detail', kwargs={'pk': instance.pk})),
                'billeterie@epita.com',
                [instance.assos_id.president.user.email],)
    
    to_pres = EmailMessage(
                'Approve an event',
                'This event needs approval.\n%s' % absoluteuri.build_absolute_uri(reverse(
                        'event:event_detail', kwargs={'pk': instance.pk})),
                'billeterie@epita.com',
                [Boss.objects.first().user.email],)


    if created:
        if instance.event_state == Event.PENDING:
            to_pres.send()
        elif instance.event_state == Event.VALIDATED:
            to_boss.send()
    else:
        if instance.was_modified():
            modified_procedure(instance)

    if instance.event_state == Event.APPROVED or (instance.event_state == instance.__old_event_state and instance.event_state == Event.PENDING):
        instance.__old_title = instance.title
        instance.__old_start = instance.start
        instance.__old_end = instance.end
        instance.__old_ticket_deadline = instance.ticket_deadline

    if (instance.event_state != instance.__old_event_state and
            instance.event_state == Event.PENDING):
        instance.title = instance.__old_title
        instance.start = instance.__old_start
        instance.end = instance.__old_end
        instance.__old_ticket_deadline = instance.ticket_deadline

    instance.__old_event_state = instance.event_state



@receiver(pre_save, sender=Event)
def send_email_event_pre(sender, instance, **kwargs): 
    if instance.pk is None:
        if instance.ticket_deadline is None:
            instance.ticket_deadline = instance.start
            instance.__old_ticket_deadline = instance.ticket_deadline


def modified_procedure(instance):

    if instance.__old_event_state == instance.event_state and instance.event_state == Event.PENDING:
        return

    header = "This event was modified:\n%s" % absoluteuri.build_absolute_uri(
            reverse('event:event_detail', kwargs={'pk': instance.pk})) 

    content = ""
    if instance.__old_title != instance.title:
        content += "\nTitle was changed from %s to %s" % (instance.__old_title,
                                                          instance.title)
    if instance.__old_start != instance.start or instance.__old_end != instance.end :
        content += "\nDates for the event were changed from\n [%s | %s] to [%s | %s]" % \
                (instance.__old_start, instance.__old_end, instance.start, instance.end)
    if instance.__old_ticket_deadline != instance.ticket_deadline :
        content += "\nThe deadline to buy tickets was changed from %s to %s" % \
                (instance.__old_ticket_deadline, instance.ticket_deadline)
    if instance.event_state == Event.VALIDATED:
        send_mail(
            'Re-Approve an event',
            header + content,
            'billeterie@epita.com',
            [Boss.objects.first().user.email],
            fail_silently=False,)
        return

    price_msg = ""
    price_modified = False
    for price in instance.prices.all():
        if price.__old_price != price.price:
            price_modified = True
            price_msg += "\nPrice for %s tickets was changed from %s€ to %s€" % \
                    (price.__old_price, price.price)

    if instance.event_state == Event.PENDING:
        send_mail(
            'Re-Approve an event',
            header + content + price_modified,
            'billeterie@epita.com',
            [Boss.objects.first().user.email],
            fail_silently=False,)

    elif instance.event_state == Event.APPROVED:
        send_mail(
            'Modified event',
            header + content + price_modified,
            'billeterie@epita.com',
            [participant.user.email for participant in instance.participants.all()],
            fail_silently=False,)


@receiver(post_init, sender=Event)
def old_fields_event(sender, instance, **kwargs):
    instance.__old_event_state = instance.event_state
    instance.__old_title = instance.title
    instance.__old_start = instance.start
    instance.__old_end = instance.end
    instance.__old_ticket_deadline = instance.ticket_deadline


@receiver(post_save, sender=Event)
def save_event_price(sender, instance, **kwargs):
    for price in instance.prices.all():
        price.save()

@receiver(post_save, sender=Price)
def save_price(sender, instance, **kwargs):
    instance.__old_price = instance.price

@receiver(post_init, sender=Price)
def old_fields_price(sender, instance, **kwargs):
    if instance.event_id.event_state == Event.APPROVED:
        instance.__old_price = instance.price
"""
