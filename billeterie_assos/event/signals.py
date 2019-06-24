from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from event.models import Profile, Event, Boss
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
def send_email_event(sender, instance, created, **kwargs):
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
