# Generated by Django 3.1.1 on 2020-10-26 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Name for the category. Limited to 255 characters.', max_length=255)),
                ('weight', models.PositiveSmallIntegerField(blank=True, db_index=True, default=0, help_text='Priority for display of several categories Lower value orders first. 0 to 32767.')),
                ('slug', models.SlugField(help_text='Short name for use in urls.', max_length=64)),
                ('description', models.CharField(blank=True, default='', help_text='Description of the category. Limited to 255 characters.', max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TermParent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tid', models.IntegerField(db_index=True, help_text='Category parented by another category.', verbose_name='term id')),
                ('pid', models.IntegerField(blank=True, db_index=True, default=-1, help_text='Category parenting another category.', verbose_name='parent term id')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
