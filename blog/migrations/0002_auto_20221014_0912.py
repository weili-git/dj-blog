# Generated by Django 3.2.15 on 2022-10-14 09:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=128, unique=True, verbose_name='类别')),
                ('count', models.IntegerField(verbose_name='文章数')),
            ],
            options={
                'verbose_name': '分类',
            },
        ),
        migrations.AlterField(
            model_name='article',
            name='category',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='blog.category', verbose_name='分类'),
        ),
    ]
