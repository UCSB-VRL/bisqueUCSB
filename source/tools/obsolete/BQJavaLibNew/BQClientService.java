/***************************************************************************
 *   Copyright (C) 2008 by Center for Bio-Image Informatics UCSB           *
 *                                                                         *
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *   This program is distributed in the hope that it will be useful,       *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU General Public License for more details.                          *
 *                                                                         *
 *   You should have received a copy of the GNU General Public License     *
 *   along with this program; if not, write to the                         *
 *   Free Software Foundation, Inc.,                                       *
 *   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
 ***************************************************************************/
package bisque;
import java.util.Iterator;
import java.util.HashMap;

public class BQClientService extends BQXMLService {

    public enum SERVICES {data_server, module_server}

    String top_uri;
    String server_uri;
    public BQDataService ds;
    private HashMap services;

    public BQClientService (String topuri_){
        top_uri = topuri_;
        server_uri = topuri_ + "/bisquik";
        services  = new HashMap();
        services.put("client_service", this);
    }
    public BQMex begin_session(String moduleID) {
        System.out.println(server_uri + "/begin_session?module_id="+moduleID);
        return (BQMex)load(server_uri + "/begin_session?module_id="+moduleID, "GET");
    }
    public void initialize_services() {
        BQResource conf = BQDataService.load(top_uri + "/bisquik/config");

        Iterator<BQResource> chi = conf.children.iterator();
        while (chi.hasNext()) {
            BQResource ch = chi.next();
            if(ch.type != null && ch.uri != null)
                System.out.println(ch.type +";"+ ch.uri);
                switch (SERVICES.valueOf(ch.type)) {
                    case data_server : services.put("data_service", new BQDataService(ch.uri)); break;
                    //case module_server : services.put("data_service", new BQModuleService(ch.uri)); break;
                }
        }
    }
    public BQXMLService get_service(String service_type) {
        return (BQXMLService)services.get (service_type);
    }
}
