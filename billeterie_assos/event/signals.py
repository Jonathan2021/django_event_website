from django.db.models.signals import post_save, post_init, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from event.models import Profile, Event, Boss, Price
from django.core.mail import send_mail
from django.urls import reverse
import absoluteuri


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=Event)  # maybe cleaner to create email object and modify it with if then send it
def send_email_event_post(sender, instance, created, **kwargs):
    if created:
        if instance.event_state == Event.PENDING:
            send_mail(
                'Validate an event',
                'This event needs validation.\n%s' % absoluteuri.build_absolute_uri(reverse(
                        'event:event_detail', kwargs={'pk': instance.pk})),
                'billeterie@epita.com',
                [instance.assos_id.president.user.email],
                fail_silently=False,)
        elif instance.event_state == Event.VALIDATED:
            send_mail(
                'Approve an event',
                'This event needs approval.\n%s' % absoluteuri.build_absolute_uri(reverse(
                        'event:event_detail', kwargs={'pk': instance.pk})),
                'billeterie@epita.com',
                [Boss.objects.first().user.email],
                fail_silently=False,)
    
    instance.__old_event_state = instance.event_state
    instance.__old_title = instance.title
    instance.__old_manager_id = instance.manager_id
    instance.__old_start = instance.start
    instance.__old_end = instance.end
    instance.__old_ticket_deadline = instance.ticket_deadline
    instance.__old_assos_id = instance.assos_id
    instance.__old_address_id = instance.address_id
    instance.__old_premium_flag = instance.permium
    instance.__old_image = instance.image
    instance.__old_see_remaining = instance.see_remaining



@receiver(pre_save, sender=Event)
def send_email_event_pre(sender, instance, **kwargs): 
    if instance.pk is None:
        if instance.ticket_deadline is None:
            instance.ticket_deadline = instance.start
            instance.__old_ticket_deadline = instance.ticket_deadline
        return

    modified = False

    header = "This event was modified:\n%s" % absoluteuri.build_absolute_uri(
            reverse('event:event_detail', kwargs={'pk': instance.pk})) 

    content = ""
    if instance.__old_title != instance.title:
        modified = True
        content += "\nTitle was changed from %s to %s" % (instance.__old_title,
                                                          instance.title)
    if instance.__old_start != instance.start or instance.__old_end != instance.end :
        modified = True
        content += "\nDates for the event were changed from\n [%s | %s] to [%s | %s]" % \
                (instance.__old_start, instance.__old_end, instance.start, instance.end)
    if instance.__old_ticket_deadline != instance.ticket_deadline :
        modified = True
        content += "\nThe deadline to buy tickets was changed from %s to %s" % \
                (instance.__old_ticket_deadline, instance.ticket_deadline)
    if modified:
        send_mail(
            'Re-Approve an event',
            header + content,
            'billeterie@epita.com',
            [Boss.objects.first().user.email],
            fail_silently=False,)

    price_msg = ""
    price_modified = False
    for price in instance.prices.all():
        if price.__old_price != price.price:
            price_modified = True
            price_msg += "\nPrice for %s tickets was changed from %s€ to %s€" % \
                    (price.__old_price, price.price)
    if modified or price_modified:
        send_mail(
            'Re-Approve an event',
            header + content + price_modified,
            'billeterie@epita.com',
            [Boss.objects.first().user.email],
            fail_silently=False,)

    if price_modified:
        send_mail(
            'Re-Approve an event',
            header + content + price_modified,
            'billeterie@epita.com',
            [participant.user.email for participant in instance.participants.all()],
            fail_silently=False,)


@receiver(post_init, sender=Event)
def old_fields_event(sender, instance, **kwargs):
    instance.__old_event_state = instance.event_state
    instance.__old_title = instance.title
    instance.__old_manager_id = instance.manager_id
    instance.__old_start = instance.start
    instance.__old_end = instance.end
    instance.__old_ticket_deadline = instance.ticket_deadline
    instance.__old_assos_id = instance.assos_id
    instance.__old_address_id = instance.address_id
    instance.__old_premium_flag = instance.permium
    instance.__old_image = instance.image
    instance.__old_see_remaining = instance.see_remaining


@receiver(post_save, sender=Event)
def save_event_price(sender, instance, **kwargs):
    for price in instance.prices.all():
        price.save()

@receiver(post_save, sender=Price)
def save_price(sender, instance, **kwargs):
    instance.__old_price = instance.price

@receiver(post_init, sender=Price)
def old_fields_price(sender, instance, **kwargs):
    instance.__old_price = instance.price
