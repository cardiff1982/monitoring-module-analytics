import enum


class Team:
    """
    Class to represent team with servers. 2 params: Team name and list of teams servers
    """

    def __init__(self, name):
        """
        Class constructor. Needs only name on generating. Servers lists initializing as empty lists
        :param name: str param (server name)
        """
        self.__name = name
        self.__servers = []

    @property
    def name(self):
        return self.__name

    @property
    def servers(self):
        return self.__servers

    @name.setter
    def name(self, name: str):
        self.__name = name

    @servers.setter
    def servers(self, servers: list):
        self.__servers = servers


class Server:
    """
    Class to represent server with metrics
    """
    def __init__(self, name: str):
        """
        Constructor for server class.  Needs only name on generating. Metrics lists initializing as empty lists
        :param name: str param (server name)
        """
        self.__name = name
        self.__cpu_metrics = []
        self.__ram_metrics = []
        self.__netflow_metrics = []

    @property
    def name(self):
        return self.__name

    @property
    def cpu_metrics(self):
        return self.__cpu_metrics

    @property
    def ram_metrics(self):
        return self.__ram_metrics

    @property
    def netflow_metrics(self):
        return self.__netflow_metrics

    @cpu_metrics.setter
    def cpu_metrics(self, metric):
        self.__cpu_metrics.append(metric)

    @ram_metrics.setter
    def ram_metrics(self, metric):
        self.__ram_metrics.append(metric)

    @netflow_metrics.setter
    def netflow_metrics(self, metric):
        self.__netflow_metrics.append(metric)


class Intensity(enum.Enum):
    """
    Enum for server intensity params (avoiding hardcoding in functions)
    """
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    EXTREME = "Extreme"


class UsageTypes(enum.Enum):
    """
    Enym for server usage types param (avoiding hardcoding in functions)
    """
    LOW = "Low"
    STABLE = "Stable"
    JUMPS = "Jumps"


class Decisions(enum.Enum):
    """
    Enum to represent possible decisions about resources (avoiding hardcoding in functions)
    """
    NORMAL = "normal using"
    DELETE = "delete resource"
    EXTEND = "extend resource"
