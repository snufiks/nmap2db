#!/usr/bin/env python
#
# Copyright (c) 2014 Rafael Martinez Guerrero (PostgreSQL-es)
# rafael@postgresql.org.es / http://www.postgresql.org.es/
#
# This file is part of Nmap2db
# https://github.com/rafaelma/nmap2db
#
# Nmap2db is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Nmap2db is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Nmap2db.  If not, see <http://www.gnu.org/licenses/>.

import sys
import psycopg2
import psycopg2.extensions
from psycopg2.extras import wait_select

from nmap2db.prettytable import *

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

#
# Class: pg_database
#
# This class is used to interact with a postgreSQL database
# It is used to open and close connections to the database
# and to set/get some information for/of the connection.
# 

class nmap2db_db():
    """This class is used to interact with a postgreSQL database"""

    # ############################################
    # Constructor
    # ############################################

    def __init__(self, dsn,logs,application):
        """ The Constructor."""

        self.dsn = dsn
        self.logs = logs
        self.application = application
        self.conn = None
        self.server_version = None
        self.cur = None

        self.output_format = 'table'

       
    # ############################################
    # Method pg_connect()
    #
    # A generic function to connect to PostgreSQL using Psycopg2
    # We will define the application_name parameter if it is not
    # defined in the DSN and the postgreSQL server version >= 9.0
    # ############################################

    def pg_connect(self):
        """A generic function to connect to PostgreSQL using Psycopg2"""

        try:
            self.conn = psycopg2.connect(self.dsn)
        
            if self.conn:
                self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
                wait_select(self.conn)

                self.cur = self.conn.cursor()

                self.server_version = self.conn.server_version

                if (self.server_version >= 90000 and 'application_name=' not in self.dsn):
              
                    try:
                        self.cur.execute('SET application_name TO %s',(self.application,))
                        self.conn.commit()
                    except psycopg2.Error as e:
                        self.logs.logger.error('Could not define the application_name parameter: - %s', e)
     
        except psycopg2.Error as e:
            raise e

    # ############################################
    # Method pg_close()
    # ############################################

    def pg_close(self):
        """A generic function to close a postgreSQL connection using Psycopg2"""

        if self.cur:
            try:
                self.cur.close()
            except psycopg2.Error as e:
                print "\n* ERROR - Could not close the cursor used in this connection: \n%s" % e    

        if self.conn:
            try:
                self.conn.close() 
            except psycopg2.Error as e:
                print "\n* ERROR - Could not close the connection to the database: \n%s" % e    
                

    # ############################################
    # Method 
    # ############################################

    def show_network_definitions(self):
        """A function to get a list with the networks defined in the system"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    self.cur.execute('SELECT * FROM show_network_definitions')
                    self.conn.commit()

                    colnames = [desc[0] for desc in self.cur.description]
                    self.print_results(self.cur,colnames,["Network","Remarks"])

                except psycopg2.Error as e:
                    raise e
                
            self.pg_close()
            
        except psycopg2.Error as e:
            raise e


    # ############################################
    # Method 
    # ############################################

    def show_scan_definitions(self):
        """A function to get a list with the scans defined in the system"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    self.cur.execute('SELECT * FROM show_scan_definitions')
                    self.conn.commit()

                    colnames = [desc[0] for desc in self.cur.description]
                    self.print_results(self.cur,colnames,["ScanID","Remarks","Arguments"])

                except psycopg2.Error as e:
                    raise e
                
            self.pg_close()
            
        except psycopg2.Error as e:
            raise e

    # ############################################
    # Method 
    # ############################################

    def show_scan_jobs(self,network_cidr):
        """A function to get a list with the scans jobs defined in the system"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    if network_cidr == 'ALL':
                        self.cur.execute('SELECT * FROM show_scan_jobs')
                        self.conn.commit()
                    else:
                        self.cur.execute('SELECT * FROM show_scan_jobs WHERE "Network" = %s',(network_cidr,))
                        self.conn.commit()

                    colnames = [desc[0] for desc in self.cur.description]
                    self.print_results(self.cur,colnames,["ScanID","Remarks","Arguments"])

                except psycopg2.Error as e:
                    raise e
                
            self.pg_close()
            
        except psycopg2.Error as e:
            raise e


    # ############################################
    # Method 
    # ############################################

    def show_host_reports(self,host,from_timestamp,to_timestamp):
        """A function to get a list or scan reports for a host"""

        try:
            self.pg_connect()

            if self.cur:
                try:

                    if (host.replace('.','')).replace('/','').isdigit():
                        self.cur.execute('SELECT * FROM show_host_reports WHERE "IPaddress" = %s AND "Registered" >= %s AND "Registered" <= %s',(host,from_timestamp, to_timestamp))
                    else:
                        self.cur.execute('SELECT * FROM show_host_reports WHERE "Hostname" @> %s AND "Registered" >= %s AND "Registered" <= %s',([host],from_timestamp, to_timestamp)) 

                    self.conn.commit()

                    colnames = [desc[0] for desc in self.cur.description]
                    self.print_results(self.cur,colnames,["ScanID","Finished","Duration","IPaddress","Hostname","State"])

                except psycopg2.Error as e:
                    raise e
                
            self.pg_close()
            
        except psycopg2.Error as e:
            raise e

    # ############################################
    # Method 
    # ############################################

    def show_host_details(self,report_id):
        """A function to get host details for a reportID"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    self.cur.execute('SELECT * FROM show_host_details WHERE "ReportID" = %s',(report_id,))
                    self.conn.commit()

                    x = PrettyTable([".",".."],header = False)
                    x.align["."] = "r"
                    x.align[".."] = "l"
                    x.padding_width = 1

                    for record in self.cur:
                        
                        x.add_row(["ReportID:",record[0]])
                        x.add_row(["Registered:",str(record[1])])
                        x.add_row(["ScanID:",record[2]])
                        x.add_row(["",""])
                        x.add_row(["Network:",record[3]])
                        x.add_row(["Network info:",record[4]])
                        x.add_row(["",""])
                        x.add_row(["IPaddress:",record[5]])
                        x.add_row(["Addrtype:",record[6]])
                        x.add_row(["Hostname:",record[7]])
                        x.add_row(["Hostname type:",record[8]])
                        x.add_row(["",""])
                        x.add_row(["OStype:",record[9]])
                        x.add_row(["OSvendor:",record[10]])
                        x.add_row(["OSfamily:",record[11]])
                        x.add_row(["OSgen:",record[12]])
                        x.add_row(["OSname:",record[13]])
                        x.add_row(["",""])
                        x.add_row(["State:",record[14]])
                        x.add_row(["State reason:",record[15]])

                        print x

                except psycopg2.Error as e:
                    raise e
                
            self.pg_close()
            
        except psycopg2.Error as e:
            raise e


    # ############################################
    # Method 
    # ############################################

    def show_services_details(self,report_id):
        """A function to get a list of services found in a scan report"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    self.cur.execute('SELECT "Prot","Port","State","Reason","Service","Method","Product","Prod.ver","Prod.info" FROM show_services_details WHERE report_id = %s',(report_id,))
                    self.conn.commit()

                    colnames = [desc[0] for desc in self.cur.description]
                    self.print_results(self.cur,colnames,["Port","State","Reason","Service","Method","Product","Prod.ver","Prod.info"])

                except psycopg2.Error as e:
                    raise e
                
            self.pg_close()
            
        except psycopg2.Error as e:
            raise e

    # ############################################
    # Method 
    # ############################################

    def show_ports(self,network_list,port_list,service_list,from_timestamp,to_timestamp):
        """A function to get a list of ports"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    
                    if network_list != None:
                        network_sql = 'AND (FALSE '
                        
                        for network in network_list:
                            network_sql = network_sql + 'OR "IPaddress" <<= \'' + network + '\' '  
                                                    
                        network_sql = network_sql + ') '

                    else:
                        network_sql = ''

                    if port_list != None:
                        port_sql = 'AND "Port" IN (' + ','.join(port_list) + ') '
                    else:
                        port_sql = ''

                    if service_list != None:
                        service_sql = 'AND (FALSE '
                        
                        for service in service_list:
                            service_sql = service_sql + 'OR "Service" LIKE \'' + service + '\' ' 

                        service_sql = service_sql + ') '
                    else:
                        service_sql = ''    
                        

                    self.cur.execute('WITH port_list AS(' + 
                                     'SELECT DISTINCT ON ("Port","Prot","IPaddress") ' +
                                     '"IPaddress",' +
                                     '"Port",' +
                                     '"Prot",' +
                                     '"State",' +
                                     '"Service",' +
                                     '"Product",' +
                                     '"Prod.ver",' +
                                     '"Prod.info" ' +
                                     'FROM show_ports ' +
                                     'WHERE registered >= \'' + str(from_timestamp) + '\' AND registered <= \'' + str(to_timestamp) + '\' ' +
                                     network_sql +
                                     port_sql + 
                                     service_sql + ')' +
                                     'SELECT DISTINCT ON ("Port","Prot","IPaddress") ' + 
                                     'a."IPaddress",' +
                                     'array_to_string(b.hostname,\' \') AS "Hostname",' + 
                                     'a."Port",' +
                                     'a."Prot",' +
                                     'a."State",' +
                                     'a."Service",' +
                                     'a."Product",' +
                                     'a."Prod.ver",' +
                                     'a."Prod.info" ' +
                                     'FROM port_list a ' +
                                     'JOIN host_info b ON a."IPaddress" = b.hostaddr ' +
                                     'WHERE b.registered >= \'' + str(from_timestamp) + '\' AND b.registered <= \'' + str(to_timestamp) + '\' '
                                     )

                    self.conn.commit()

                    colnames = [desc[0] for desc in self.cur.description]
                    self.print_results(self.cur,colnames,["IPaddress","Hostname","Port","Prot","State","Service","Product","Prod.ver","Prod.info"])

                except psycopg2.Error as e:
                    raise e
                
            self.pg_close()
            
        except psycopg2.Error as e:
            raise e


    # ############################################
    # Method 
    # ############################################

    def show_os(self,network_list,os_list,from_timestamp,to_timestamp):
        """A function to get a list og hostnames running an OS"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    
                    if network_list != None:
                        network_sql = 'AND (FALSE '
                        
                        for network in network_list:
                            network_sql = network_sql + 'OR "Network" <<= \'' + network + '\' '  
                                                    
                        network_sql = network_sql + ') '

                    else:
                        network_sql = ''

                    if os_list != None:
                        os_sql = 'AND (FALSE '

                        for osname in os_list:
                            os_sql = os_sql + 'OR "OSname" LIKE \'' + osname + '\' ' 

                        os_sql = os_sql + ') '
                    else:
                        os_sql = ''


                    fullstmt = 'SELECT DISTINCT ON ("IPaddress") "Registered", "IPaddress", "Hostname",' + '"OSname" ' +  'FROM show_host_details ' + 'WHERE "Registered" >= \'' + str(from_timestamp) + '\' AND "Registered" <=  \'' + str(to_timestamp) + '\' ' + network_sql + os_sql + 'ORDER BY "IPaddress"'
                    self.logs.logger.info(fullstmt)

                    self.cur.execute(fullstmt)
                    self.conn.commit()

                    colnames = [desc[0] for desc in self.cur.description]
                    self.print_results(self.cur,colnames,["IPaddress","Hostname","OSname"])

                except psycopg2.Error as e:
                    raise e
                
            self.pg_close()
            
        except psycopg2.Error as e:
            raise e


    # ############################################
    # Method 
    # ############################################

    def show_host_without_hostname(self):
        """A function to get a list of host without a hostname"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    self.cur.execute('SELECT "IPaddress","State","Last registration" FROM show_host_without_hostname')
                    self.conn.commit()

                    colnames = [desc[0] for desc in self.cur.description]
                    self.print_results(self.cur,colnames,["IPaddress","State","Last registration"])

                except psycopg2.Error as e:
                    raise e
                
            self.pg_close()
            
        except psycopg2.Error as e:
            raise e

    # ############################################
    # Method 
    # ############################################

    def register_network(self,network_cidr,remarks):
        """A method to register a network_cidr"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    self.cur.execute('SELECT register_network(%s,%s)',(network_cidr,remarks))
                    self.conn.commit()                        
                
                except psycopg2.Error as  e:
                    raise e

            self.pg_close()

        except psycopg2.Error as e:
            raise e


    # ############################################
    # Method 
    # ############################################

    def register_scan_job(self,network_cidr,scan_id,execution_interval,is_active):
        """A method to register a scan job"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    self.cur.execute('SELECT register_scan_job(%s,%s,%s,%s)',(network_cidr,scan_id,execution_interval,is_active))
                    self.conn.commit()                        
                
                except psycopg2.Error as  e:
                    raise e

            self.pg_close()

        except psycopg2.Error as e:
            raise e

    # ############################################
    # Method 
    # ############################################

    def get_next_scan_job(self):
        """A method to get the next scan job to run"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    self.cur.execute('SELECT get_next_scan_job()')
                    self.conn.commit()                        
                
                    scan_job_id = self.cur.fetchone()[0]
                    return scan_job_id
                    
                except psycopg2.Error as  e:
                    raise e

            self.pg_close()

        except psycopg2.Error as e:
            raise e

    # ############################################
    # Method 
    # ############################################

    def get_scan_job_args(self,scan_job_id):
        """A method to get the arguments for a scan_job"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    self.cur.execute('SELECT get_scan_job_args(%s)',(scan_job_id,))
                    self.conn.commit()                        
                
                    scan_job_args = self.cur.fetchone()[0]
                    return scan_job_args
                    
                except psycopg2.Error as  e:
                    raise e

            self.pg_close()

        except psycopg2.Error as e:
            raise e

    # ############################################
    # Method get_scan_job_command
    # ############################################

    def get_scan_job_command(self,scan_job_id):
        """A method to get the scan executable for a scan_job"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    self.cur.execute('SELECT get_scan_job_command(%s)',(scan_job_id,))
                    self.conn.commit()

                    scan_job_command = self.cur.fetchone()[0]
                    return scan_job_command

                except psycopg2.Error as  e:
                    raise e

            self.pg_close()

        except psycopg2.Error as e:
            raise e

    # ############################################
    # Method get_scan_job_parsemethod
    # ############################################

    def get_scan_job_parsemethod(self,scan_job_id):
        """A method to get the parse method for a scan_job"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    self.cur.execute('SELECT get_scan_job_parsemethod(%s)',(scan_job_id,))
                    self.conn.commit()

                    scan_job_parsemethod = self.cur.fetchone()[0]
                    return scan_job_parsemethod

                except psycopg2.Error as  e:
                    raise e

            self.pg_close()

        except psycopg2.Error as e:
            raise e

    # ############################################
    # Method 
    # ############################################

    def get_scan_job_network(self,scan_job_id):
        """A method to get the network for a scan_job"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    self.cur.execute('SELECT get_scan_job_network_addr(%s)',(scan_job_id,))
                    self.conn.commit()

                    scan_job_network = self.cur.fetchone()[0]
                    return scan_job_network

                except psycopg2.Error as  e:
                    raise e

            self.pg_close()

        except psycopg2.Error as e:
            raise e

    # ############################################
    # Method get_scan_job_scope
    # ############################################

    def get_scan_job_scope(self,scan_job_id):
        """A method to get the scan scope for a scan_job"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    query = "SELECT scan_scope FROM scan_job WHERE id=%s"
                    self.logs.logger.info("SELECT scan_scope FROM scan_job WHERE id=%d",scan_job_id)
                    self.cur.execute(query, [scan_job_id])
                    self.conn.commit()

                    scan_job_scope = self.cur.fetchone()[0]
                    return scan_job_scope

                except psycopg2.Error as  e:
                    raise e

            self.pg_close()

        except psycopg2.Error as e:
            raise e

    # ############################################
    # Method 
    # ############################################

    def save_scan_report(self,scan_job_id, report, scan_type):
        """A method to save a scan report"""

        # self.logs.logger.info("save_scan_report PRE _%s_", scan_type)
        sqlstmt = False
        if scan_type == 'nmap_default':
            # self.logs.logger.info("save_scan_report (nmap_default) _%s_", scan_type)
            sqlstmt = 'SELECT save_scan_report_xml(%s,%s)'
        elif scan_type == 'testssl':
            # self.logs.logger.info("save_scan_report (testssl) _%s_", scan_type)
            sqlstmt = 'SELECT save_ssl_report_json(%s,%s)'
        else:
            self.logs.logger.info("save_scan_report ELSE _%s_", scan_type)

        # self.logs.logger.info("save_scan_report (report) _%s_", report)
        # self.logs.logger.info("save_scan_report (scan_job_id) _%s_", scan_job_id)

        try:
            self.pg_connect()

            if self.cur and sqlstmt:
                try:
                    # self.logs.logger.info("save_scan_report (sqlstmt) _%s_", sqlstmt)
                    self.cur.execute(sqlstmt, (scan_job_id, report))
                    self.conn.commit()                        
                
                    return True
                except psycopg2.Error as  e:
                    raise e

            self.pg_close()

        except psycopg2.Error as e:
            raise e


    # ############################################
    # Method 
    # ############################################

    def expand_network(self,scan_job_network):
        """A method to get all IPs in a network"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    self.cur.execute('SELECT expand_network(%s)',(scan_job_network,))
                    self.conn.commit()                        
                
                    return self.cur
                    
                except psycopg2.Error as  e:
                    raise e

            self.pg_close()

        except psycopg2.Error as e:
            raise e

    # ############################################
    # Method 
    # ############################################
            
    def print_results(self,cur,colnames,left_columns):
        '''A function to print a table with sql results'''

        if self.output_format == 'table':

            x = PrettyTable(colnames)
            x.padding_width = 1
            
            for column in left_columns:
                x.align[column] = "l"
        
            for records in cur:
                columns = []

                for index in range(len(colnames)):
                    columns.append(records[index])

                x.add_row(columns)
            
            print x.get_string()
            print

        elif self.output_format == 'csv':
            
            for records in cur:
                columns = []

                for index in range(len(colnames)):
                    columns.append(str(records[index]))

                print ','.join(columns)



    # ############################################
    # Method 
    # ############################################

    def show_hosts(self):
        """A function to get a list with the scans defined in the system"""

        try:
            self.pg_connect()

            if self.cur:
                try:
                    self.cur.execute('SELECT "IP-address","Hostname","Last registration", "First registration" FROM show_hosts')
                    self.conn.commit()

                    colnames = [desc[0] for desc in self.cur.description]
                    self.print_results(self.cur,colnames,["IP-address","Hostname","Last registration", "First registration"])

                except psycopg2.Error as e:
                    raise e
                
            self.pg_close()
            
        except psycopg2.Error as e:
            raise e
                
