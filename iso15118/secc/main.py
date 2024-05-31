import asyncio
import logging

from iso15118.secc import SECCHandler
from iso15118.secc.controller.interface import ServiceStatus
from iso15118.secc.controller.simulator import SimEVSEController
from iso15118.secc.secc_settings import Config
from iso15118.shared.exificient_exi_codec import ExificientEXICodec
from iso15118.secc.controller.evse_data_remote_node import evseDataRemoteNode
from iso15118.shared.settings import load_shared_settings, shared_settings
#from iso15118.secc.transport.tcp_server import TCPServer
logger = logging.getLogger(__name__)


async def main():
    """
    Entrypoint function that starts the ISO 15118 code running on
    the SECC (Supply Equipment Communication Controller)
    """
    config = Config()
    config.load_envs()
    config.print_settings()

    #rcv_queue: asyncio.Queue = asyncio.Queue()
    #server_ready_event: asyncio.Event = asyncio.Event()
    #tcp_server = TCPServer(rcv_queue, "eth1")
    #await tcp_server.start_tls(server_ready_event)

    sim_evse_controller = SimEVSEController()
    evseDataRNode = evseDataRemoteNode(config, sim_evse_controller)
    shared_settings["evseDataRemoteNode"] = evseDataRNode
    await sim_evse_controller.set_status(ServiceStatus.STARTING)
    await SECCHandler(
        exi_codec=ExificientEXICodec(),
        evse_controller=sim_evse_controller,
        config=config,
    ).start(config.iface)


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.debug("SECC program terminated manually")


if __name__ == "__main__":
    run()
