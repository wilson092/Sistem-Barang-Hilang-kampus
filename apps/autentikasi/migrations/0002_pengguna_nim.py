from django.db import migrations, models


def isi_nim_pengguna_lama(apps, schema_editor):
    Pengguna = apps.get_model("autentikasi", "Pengguna")
    for pengguna in Pengguna.objects.using(schema_editor.connection.alias).all().iterator():
        # Pakai username sebagai NIM sementara agar akun lama tetap dapat dipakai login.
        # Username yang terlalu panjang mendapat kode migrasi yang tetap unik.
        nim = pengguna.username if len(pengguna.username) <= 30 else f"LEGACY{pengguna.pk}"
        pengguna.nim = nim
        pengguna.save(update_fields=["nim"])


class Migration(migrations.Migration):
    dependencies = [("autentikasi", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="pengguna",
            name="nim",
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.RunPython(isi_nim_pengguna_lama, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="pengguna",
            name="nim",
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
