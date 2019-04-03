# Generated by Django 2.1 on 2019-04-02 14:45

from django.db import migrations, models
import django.db.models.deletion

# (SCALE_DATA, 'data to reference'),
# (SCALE_REF, 'reference to data')
SCALE_DATA = 'data'
SCALE_REF = 'ref'

# see: https://docs.djangoproject.com/en/2.1/topics/migrations/#data-migrations
def update_validation_runs(apps, schema_editor):
    # We can't import the ValidationRun model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    ValidationRun = apps.get_model('validator', 'ValidationRun')
    DatasetConfiguration = apps.get_model('validator', 'DatasetConfiguration')
    for run in ValidationRun.objects.all():
        
        dataset_c = DatasetConfiguration()
        dataset_c.validation = run
        dataset_c.dataset = run.data_dataset
        dataset_c.version = run.data_version
        dataset_c.variable = run.data_variable
        dataset_c.save()

        dataset_c.filters.set(run.data_filters.all())
        dataset_c.save()
        
        reference_c = DatasetConfiguration()
        reference_c.validation = run
        reference_c.dataset = run.ref_dataset
        reference_c.version = run.ref_version
        if run.ref_variable:
            reference_c.variable = run.ref_variable
        else:
            print("\nWARNING Validation run {} has no reference variable".format(run))
            run.delete()
            dataset_c.delete()
            continue

        reference_c.save()

        reference_c.filters.set(run.ref_filters.all())
        reference_c.save()
        
        run.reference_configuration = reference_c
        
        if run.scaling_ref == SCALE_DATA:
            run.scaling_ref = reference_c
        else:
            run.scaling_ref = dataset_c
        
        run.save()

class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0003_celery_task_20190402_1445'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatasetConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dataset_configurations', to='validator.Dataset')),
                ('filters', models.ManyToManyField(related_name='dataset_configurations', to='validator.DataFilter')),
            ],
        ),
        migrations.AddField(
            model_name='datasetconfiguration',
            name='validation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dataset_configurations', to='validator.ValidationRun'),
        ),
        migrations.AddField(
            model_name='datasetconfiguration',
            name='variable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dataset_configurations', to='validator.DataVariable'),
        ),
        migrations.AddField(
            model_name='datasetconfiguration',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dataset_configurations', to='validator.DatasetVersion'),
        ),
        migrations.RenameField(
            model_name='validationrun',
            old_name='scaling_ref',
            new_name='old_scaling_ref'
            ),
        migrations.AddField(
            model_name='validationrun',
            name='scaling_ref',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='scaling_ref_validation_run', to='validator.DatasetConfiguration'),
        ),
        migrations.AddField(
            model_name='validationrun',
            name='reference_configuration',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ref_validation_run', to='validator.DatasetConfiguration'),
        ),        
        
        migrations.RunPython(update_validation_runs),        
    ]