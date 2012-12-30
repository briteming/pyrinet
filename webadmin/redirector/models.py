from webadm import BaseModel
from sqlalchemy import *


class Redirector(BaseModel):
    __tablename__ = 'redirectors'
    TCP = 0
    UDP = 1

    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean, default=True)
    protocol = Column(Integer, default=0)
    local_ip = Column(String(16))
    local_port = Column(Integer)
    remote_ip = Column(String(16))
    remote_port = Column(Integer)

    def copy_form(self, rd):
        self.protocol = self.TCP if rd.protocol.data == 'tcp' else self.UDP
        self.local_ip = rd.local_ip.data
        self.local_port = rd.local_port.data
        self.remote_ip = rd.remote_ip.data
        self.remote_port = rd.remote_port.data

    def dump(self):
        return {'protocol': 'tcp' if self.protocol == self.TCP else 'udp',
            'local': '%s:%d' % (self.local_ip, self.local_port),
            'remote': '%s:%d' % (self.remote_ip, self.remote_port),
            'enabled': self.enabled, 'id': self.id}
