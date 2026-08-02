from django.db import models
import uuid

from django.core.exceptions import ValidationError

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length = 30, unique=True)
    rooms = models.ManyToManyField('Room', blank=True)
    friends = models.ManyToManyField('self', symmetrical=True, blank=True)
    public_key = models.BinaryField()
    private_key = models.BinaryField()

    def generate_key_pair(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        self.public_key = public_key
        self.private_key = private_key_bytes
        self.save()

    def __str__(self) -> str:
        return self.name



class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def clean(self):
        if self.from_user == self.to_user:
            raise ValidationError("You cannot send a friend request to your self")
        
        if  self.from_user in self.to_user.friends.all():
            raise ValidationError("You cannot send a friend request to your friend")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super(FriendRequest, self).save(*args, **kwargs)



class Room(models.Model):
    members = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)
    room_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    shared_key = models.BinaryField()  # Store the shared key for the room

    def generate_shared_key(self):
        # Generate the shared key using some key exchange algorithm like Diffie-Hellman
        # For simplicity, you could just concatenate and hash the public keys of all members
        members_public_keys = [member.public_key for member in self.members.all()]
        concatenated_public_keys = b''.join(members_public_keys)
        shared_key = hashes.Hash(hashes.SHA256())
        shared_key.update(concatenated_public_keys)
        self.shared_key = shared_key.finalize()
        self.save()
    
    def get_room_name(self, user):
        room_name = [member.name for member in self.members.all() if member != user]
        return ",".join(room_name)


class Messages(models.Model):
    conversation = models.ForeignKey(Room, related_name="conversation", on_delete=models.CASCADE)
    content = models.CharField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ("created_at",)
    
    def clean(self):
        if self.created_by not in self.conversation.members.all():
            raise ValidationError("The user is not a member of this group")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super(Messages, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.content
