# Generated by Django 3.1.1 on 2021-09-10 13:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.FileField(upload_to='uploads/files/')),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group')),
                ('users', models.ManyToManyField(editable=False, related_name='topic_users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expiration', models.DateTimeField()),
                ('status', models.CharField(choices=[('OP', 'Open'), ('CL', 'Closed'), ('PE', 'Pending'), ('RE', 'Resolved'), ('EX', 'Expired')], default='OP', max_length=2)),
                ('content', models.TextField()),
                ('comments', models.ManyToManyField(blank=True, related_name='comments', to='api.Comment')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator', to=settings.AUTH_USER_MODEL)),
                ('groups', models.ManyToManyField(related_name='groups', to='auth.Group')),
                ('receivers', models.ManyToManyField(related_name='receivers', to=settings.AUTH_USER_MODEL)),
                ('topics', models.ManyToManyField(related_name='topics', to='api.Topic')),
                ('uploads', models.ManyToManyField(blank=True, related_name='uploads', to='api.File')),
            ],
        ),
    ]
