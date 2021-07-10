from mdutils.mdutils import MdUtils
import requests
import yaml
import Classes


def make_usage_decision(intensity: str, usage_type: str) -> str:
    """
    This finction is needed to make decision about resource, based on usage untensity and usage type
    :param intensity: usage intensity for resource
    :param usage_type: usage type for resource
    :return: descision (str)
    """
    decision = ""
    if intensity == Classes.Intensity.LOW.value or \
            (intensity == Classes.Intensity.NORMAL.value and usage_type == Classes.UsageTypes.LOW.value):
        decision = Classes.Decisions.DELETE.value

    elif intensity == Classes.Intensity.EXTREME.value or \
            (intensity == Classes.Intensity.HIGH.value and usage_type == Classes.UsageTypes.JUMPS.value):
        decision = Classes.Decisions.EXTEND.value

    elif intensity == Classes.Intensity.NORMAL.value \
            or intensity == Classes.Intensity.HIGH.value:
        decision = Classes.Decisions.NORMAL.value

    return decision


def write_report_file(teams: dict, prices: dict):
    """
    Funtion generates report in Marksdown format and outputes it to report.md file
    :param teams: dict of teams with resources
    :return:
    """
    try:
        report_file = MdUtils(file_name="report", title="Teams resources usage report")
        for team, team_data in teams.items():
            report_file.new_header(level=1, title="Team: " + team)
            report_file_data = ["Resource", "Dimension", "mean", "median", "usage_type", "intencity", "decisiion",
                                "Cost"]
            for server_name, server_data in team_data.items():
                for dimension_name, dimension_data in server_data.items():
                    decision = make_usage_decision(dimension_data["intensity"], dimension_data["usage_type"])
                    report_file_data.extend([server_name, dimension_name, str(dimension_data["mean"]),
                                             str(dimension_data["median"]), dimension_data["usage_type"],
                                             dimension_data["intensity"], decision,
                                             "" if decision != Classes.Decisions.DELETE.value
                                             else prices.get("values").get(server_name).get(dimension_name)])
            report_file.new_table(columns=8, rows=len(team_data) * len(server_data) + 1, text=report_file_data,
                                  text_align='center')
        report_file.new_header(level=1, title="Resources TCO")
        report_file_tco_data = ["Resource", "TCO"]
        for name, dimension_prices in prices.get("values").items():
            server_tco = 0
            for dimension, price in dimension_prices.items():
                server_tco += price
            report_file_tco_data.extend([name, server_tco])
        report_file.new_table(columns=2, rows=len(prices.get("values").items()) + 1, text=report_file_tco_data)
        report_file.create_md_file()
    except IOError:
        print("I/O Error")


def get_uniq_servers_names(team_servers) -> set:
    """
    Normalise servers list for every team
    :param team_servers: list of server names
    :return: set of server names for team
    """
    return set(team_server[1:-1].split(",")[0] for team_server in team_servers.split(";"))


def get_teams(raw_data) -> list:
    """
    Function to generate objects of Team class object (Class object include team name and list of servers,
    pack it intolist and return this list
    :param raw_data: unformatted data of monitoring metrics
    :return:
    """
    teams_with_data = raw_data.split("$")
    teams_list = []
    for team in teams_with_data:

        team_name, team_metrics = team.split("|")
        current_team = Classes.Team(team_name)

        for team_server_name in get_uniq_servers_names(team_metrics):
            current_server = Classes.Server(team_server_name)
            for team_metric in team_metrics.split(";"):
                server_name, servers_metric_name, metric_time, servers_metric_value = team_metric[1:-1].split(",")
                if server_name == team_server_name:
                    if servers_metric_name == "CPU":
                        current_server.cpu_metrics = int(servers_metric_value)
                    elif servers_metric_name == "RAM":
                        current_server.ram_metrics = int(servers_metric_value)
                    else:
                        current_server.netflow_metrics = int(servers_metric_value)
            current_team.servers.append(current_server)
        teams_list.append(current_team)

    return teams_list


def get_median(list_of_ints) -> float:
    """
    Function to count median for any list of ints
    :param list_of_ints: list ro count median
    :return: median (float format)
    """
    quotient, remainder = divmod(len(list_of_ints), 2)
    return list_of_ints[quotient] if remainder else sum(list_of_ints[quotient - 1: quotient + 1]) / 2


def get_usage_and_intensivity(avg, median) -> dict:
    """
    Function to get usage and intensity status for resource
    :param avg: average load for resource
    :param median: median of load for resource
    :return: dictionary with usage_type and usage_intensity keys
    """
    usage_type = Classes.UsageTypes.STABLE.value
    if avg < median * 0.75:
        usage_type = Classes.UsageTypes.LOW.value
    elif avg > median * 1.25:
        usage_type = Classes.UsageTypes.JUMPS.value

    usage_intensity = Classes.Intensity.NORMAL.value
    if 0 < median <= 30:
        usage_intensity = Classes.Intensity.LOW.value
    elif 60 < median <= 90:
        usage_intensity = Classes.Intensity.HIGH.value
    elif median > 90:
        usage_intensity = Classes.Intensity.EXTREME.value

    return {"usage_type": usage_type, "usage_intensity": usage_intensity}


def get_all_stats(metrics: list) -> tuple:
    """
    Function count and return median, average load ans usage type for metrics
    :param metrics: list of metrics values
    :return: tuple (metric median, metric avg, metric usage type)
    """
    median = get_median(metrics)
    avg = sum(metrics) / len(metrics)
    usage_data = get_usage_and_intensivity(avg=avg, median=median)

    return median, avg, usage_data


def get_server_stats(server) -> dict:
    """
    Function to get server statistics for all parameters (CPU, RAM, NETFLOW) for server
    :param server: Object of Server class
    :return: Resulting dict
    """
    cpu_median, cpu_avg, cpu_usage_data = get_all_stats(server.cpu_metrics)
    ram_median, ram_avg, ram_usage_data = get_all_stats(server.ram_metrics)
    netflow_median, netflow_avg, netflow_usage_data = get_all_stats(server.netflow_metrics)

    return {"CPU": {"mean": cpu_avg, "median": cpu_median, "usage_type": cpu_usage_data["usage_type"],
                    "intensity": cpu_usage_data["usage_intensity"]},
            "RAM": {"mean": ram_avg, "median": ram_median, "usage_type": ram_usage_data["usage_type"],
                    "intensity": ram_usage_data["usage_intensity"]},
            "NetFlow": {"mean": netflow_avg, "median": netflow_median, "usage_type": netflow_usage_data["usage_type"],
                        "intensity": netflow_usage_data["usage_intensity"]}}


def get_data():
    """
    Function to get monitoring module data via http protocol
    :return: dict with load_data and prices keys
    """
    with requests.Session() as session:
        url_load_data = "http://localhost:21122/monitoring/infrastructure/using/summary/1"
        url_prices = "http://localhost:21122//monitoring/infrastructure/using/prices"
        response_load_data = session.get(url=url_load_data)
        response_prices = session.get(url=url_prices)

    return {"load_data": response_load_data.text,
            "prices": response_prices.text}


def get_resourceprices():
    pass


def main():
    result_dict = {}
    incoming_data = get_data()
    load_data = incoming_data.get("load_data")
    resource_prices = yaml.load(incoming_data.get("prices"), Loader=yaml.FullLoader)

    teams = get_teams(load_data)
    for team in teams:
        result_dict.update({team.name: None})
        team_servers = {}
        for server in team.servers:
            servers_data = get_server_stats(server)
            team_servers.update({server.name: servers_data})
            result_dict.update({team.name: team_servers})

    write_report_file(result_dict, resource_prices)
    print(result_dict)


if __name__ == '__main__':
    main()
