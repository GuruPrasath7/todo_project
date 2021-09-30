from django.core.management import BaseCommand

from todo_app.models import User


class Command(BaseCommand):
    def setup_oauth_application(self):
        from oauth2_provider.models import Application
        application = Application.objects.filter(name='Authorization')
        if not application:
            Application.objects.create(name="Authorization",
                                       client_id="e2SWnsY41x1ePATRs6C1BxeceiKhQLjj57cvBAmk",
                                       client_type="confidential",
                                       client_secret="8yozVowcQmdb573xHt1PE68KU9ZhJ1ikymoZuUPKe0f0sPDLB218iiNRX0NbOPIrmrtalD1rwr4wRSAnPj19CyVmg2OTOFPBGwSOiKbuCpLsNFqGaAsMyuZGm8DosLiu",
                                       authorization_grant_type="password")

    def create_super_admin(self):
        super_admin_username = "superadmin@gmail.com"
        super_admin_password = "password"
        if not User.objects.filter(username=super_admin_username, is_superuser=True, is_active=True):
            user = User(username=super_admin_username, first_name="super", last_name="admin", is_superuser=True,
                        is_staff=True, is_active=True)
            user.set_password(super_admin_password)
            user.save()

    def add_arguments(self, parser):
        parser.add_argument('-o', '--only', nargs='+', type=int, help="Only run the particular process")
        parser.add_argument('-n', '--not', nargs="+", type=int, help="Not include the the particular process")

    def handle(self, *args, **options):
        build_data = {
            1: self.setup_oauth_application,
            2: self.create_super_admin
        }

        if options['only']:
            print("Running for only {} \n".format(options['only']))
            for process_id in options['only']:
                print("Started '{} - {}' process".format(process_id, build_data[process_id].__name__))
                try:
                    build_data[process_id]()
                    print("Completed '{} - {}' process".format(process_id, build_data[process_id].__name__))
                except Exception as e:
                    print(
                        "Error Occurred in '{} - {}' process - {}".format(process_id, build_data[process_id].__name__,
                                                                          e))
                print("\n")
        else:
            skip_list = options['not'] if options['not'] else []
            for key, process in build_data.items():
                if key not in skip_list:
                    print("Started '{} - {}' process....".format(key, process.__name__))
                    try:
                        process()
                        print("Completed '{} - {}' process.".format(key, process.__name__))
                    except Exception as e:
                        print("Error Occurred in '{} - {}' process - {}".format(key, process.__name__, str(e)))
                    print('\n')
        print('Completed Backend Setup')
