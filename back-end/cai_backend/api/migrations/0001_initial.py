# Generated by Django 5.1.6 on 2025-03-09 03:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                (
                    "estimated_time",
                    models.CharField(
                        choices=[
                            ("15", "15 minutes"),
                            ("30", "30 minutes"),
                            ("45", "45 minutes"),
                            ("60", "1 hour"),
                            ("90", "1.5 hours"),
                            ("120", "2 hours"),
                        ],
                        default="30",
                        max_length=3,
                    ),
                ),
                (
                    "skill_level",
                    models.CharField(
                        choices=[
                            ("Beginner", "Beginner"),
                            ("Intermediate", "Intermediate"),
                            ("Advanced", "Advanced"),
                        ],
                        default="Beginner",
                        max_length=12,
                    ),
                ),
                ("instructions", models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "available_time",
                    models.CharField(
                        choices=[
                            ("15", "15 minutes"),
                            ("30", "30 minutes"),
                            ("45", "45 minutes"),
                            ("60", "1 hour"),
                            ("90", "1.5 hours"),
                            ("120", "2 hours"),
                        ],
                        default="30",
                        max_length=3,
                    ),
                ),
                (
                    "skill_level",
                    models.CharField(
                        choices=[
                            ("Beginner", "Beginner"),
                            ("Intermediate", "Intermediate"),
                            ("Advanced", "Advanced"),
                        ],
                        default="Beginner",
                        max_length=12,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Ingredients",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ingredient", models.CharField(max_length=50)),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ingredients",
                        to="api.recipe",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DietaryRestriction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "restriction",
                    models.CharField(
                        blank=True,
                        help_text="Dietary restrictions, seperated by a comma (,)",
                        max_length=200,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dietary_restrictions",
                        to="api.user",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RegisteredUser",
            fields=[
                (
                    "user_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="api.user",
                    ),
                ),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("username", models.CharField(max_length=50)),
                ("email", models.EmailField(max_length=254)),
                ("hashed_password", models.CharField(max_length=254)),
                ("is_admin", models.BooleanField(default=False)),
                (
                    "last_used_recipes",
                    models.ManyToManyField(
                        blank=True, related_name="last_used_recipes", to="api.recipe"
                    ),
                ),
                (
                    "saved_recipes",
                    models.ManyToManyField(
                        blank=True, related_name="saved_recipes", to="api.recipe"
                    ),
                ),
            ],
            bases=("api.user",),
        ),
    ]
