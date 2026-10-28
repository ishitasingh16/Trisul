import os
import http.server
import socketserver
import threading
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
import rclpy
from rclpy.node import Node


class DashboardServerNode(Node):

    def __init__(self):
        super().__init__('dashboard_server')
        self.declare_parameter('port', 8080)
        self.port = self.get_parameter('port').get_parameter_value().integer_value

        try:
            pkg_share = get_package_share_directory('navis_dashboard')
            self.www_dir = Path(pkg_share) / 'www'
        except Exception:
            self.www_dir = Path(__file__).resolve().parents[1] / 'www'

        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()

    def run_server(self):
        os.chdir(str(self.www_dir))
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", self.port), handler) as httpd:
            httpd.serve_forever()


def main(args=None):
    rclpy.init(args=args)
    node = DashboardServerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
