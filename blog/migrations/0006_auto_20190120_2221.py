# Generated by Django 2.0 on 2019-01-20 14:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_blog_readed_num'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blog',
            old_name='readed_num',
            new_name='read_num',
        ),
    ]