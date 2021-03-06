import boto3
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []

    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

@click.group()
def cli():
    """Shotty manages snapshots"""

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project: <name>)")
def list_volumes(project): #ver que no cambio esto
    "List EC2 snapshots"
    
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")    
                )))

    return

@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project', default=None,
    help="Only volumes for project (tag Project: <name>)")
def list_volumes(project):
    "List EC2 instances"
    
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
            v.id,
            i.id,
            v.state,
            str(v.size) + "GiB",
            v.encrypted and "Encrypted" or "Not Encrypted"
            )))

    return

@cli.group(instances)
def instances():
    """Commands for instances"""

@instances.command('snapshot',
    help="Create snapshots of all volumes")
@click.option('--project', default=None,
    help="Only instances for projecy (tag Project:<name>")
def create_snapshots(project):
    "Create snapshots for EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        i.stop()
        i.wait_until_stopped()

        for v i.volumes.all():
            print("Creating snapshot of {0}".format(v.id))
            v.create_snapshots(Description="Created by CursoPython")
        
        print("Starting {0}...".format(i.id))

        i.start()
        i.wait_until_running()

    
    print("teminado")
            
    return

@instances.command('list')
@click.option('--project', default=None,
    help="Only instances for project (tag Project: <name>)")
def list_instances(project):
    "List EC2 instances"
    
    instances = filter_instances(project)
    
    for i in instances:
        tags = {t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tag.get('Project', '<no project>')
            )))
    
    return

@instances.command('stop')
@click.option('--project', default=None,
help='Only instances for project')
def stop_instances(project):
    "Stop EC2 instances"

instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        i.stop()

    return

@instances.command('start')
@click.option('--project', default=None,
help='Only instances for project')
def start_instances(project):
    "Start EC2 instances"

instances = filter_instances(project)

    for i in instances:
        print("Starting {0}...".format(i.id))
        i.start()

        return

if __name__ == '__main__':
    cli()
    

    
