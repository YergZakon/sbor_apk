"""
Maps - Утилиты для работы с картами
"""
import folium
from folium import plugins
from typing import List, Dict, Optional, Tuple
import json


def create_base_map(
    center_lat: float = 51.1694,
    center_lon: float = 71.4491,
    zoom_start: int = 10,
    tiles: str = "OpenStreetMap"
) -> folium.Map:
    """
    Создание базовой карты

    Args:
        center_lat: Широта центра карты (по умолчанию - Астана)
        center_lon: Долгота центра карты
        zoom_start: Начальный зуом
        tiles: Тип тайлов ('OpenStreetMap', 'Stamen Terrain', 'Stamen Toner', 'CartoDB positron')

    Returns:
        Folium Map
    """
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles=tiles
    )

    # Добавляем переключатель слоев
    folium.LayerControl().add_to(m)

    return m


def add_marker(
    map_obj: folium.Map,
    lat: float,
    lon: float,
    popup_text: str,
    tooltip_text: Optional[str] = None,
    icon_color: str = "blue",
    icon: str = "info-sign"
) -> folium.Map:
    """
    Добавление маркера на карту

    Args:
        map_obj: Объект карты Folium
        lat: Широта
        lon: Долгота
        popup_text: Текст всплывающего окна
        tooltip_text: Текст подсказки при наведении
        icon_color: Цвет иконки ('red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray')
        icon: Иконка (Bootstrap Glyphicons)

    Returns:
        Folium Map
    """
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=tooltip_text,
        icon=folium.Icon(color=icon_color, icon=icon)
    ).add_to(map_obj)

    return map_obj


def add_field_polygon(
    map_obj: folium.Map,
    coordinates: List[Tuple[float, float]],
    field_name: str,
    field_info: Optional[Dict] = None,
    fill_color: str = "green",
    fill_opacity: float = 0.3,
    color: str = "darkgreen",
    weight: int = 2
) -> folium.Map:
    """
    Добавление полигона поля на карту

    Args:
        map_obj: Объект карты Folium
        coordinates: Список координат [(lat, lon), ...]
        field_name: Название поля
        field_info: Дополнительная информация о поле
        fill_color: Цвет заливки
        fill_opacity: Прозрачность заливки
        color: Цвет границы
        weight: Толщина границы

    Returns:
        Folium Map
    """
    # Формирование текста popup
    popup_html = f"<b>{field_name}</b><br>"
    if field_info:
        for key, value in field_info.items():
            popup_html += f"{key}: {value}<br>"

    folium.Polygon(
        locations=coordinates,
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=field_name,
        color=color,
        weight=weight,
        fill=True,
        fill_color=fill_color,
        fill_opacity=fill_opacity
    ).add_to(map_obj)

    return map_obj


def add_circle(
    map_obj: folium.Map,
    lat: float,
    lon: float,
    radius: float,
    popup_text: str,
    color: str = "blue",
    fill_color: str = "blue",
    fill_opacity: float = 0.2
) -> folium.Map:
    """
    Добавление круга на карту

    Args:
        map_obj: Объект карты Folium
        lat: Широта центра
        lon: Долгота центра
        radius: Радиус в метрах
        popup_text: Текст всплывающего окна
        color: Цвет границы
        fill_color: Цвет заливки
        fill_opacity: Прозрачность заливки

    Returns:
        Folium Map
    """
    folium.Circle(
        location=[lat, lon],
        radius=radius,
        popup=popup_text,
        color=color,
        fill=True,
        fill_color=fill_color,
        fill_opacity=fill_opacity
    ).add_to(map_obj)

    return map_obj


def add_heatmap(
    map_obj: folium.Map,
    data: List[Tuple[float, float, float]],
    name: str = "Тепловая карта"
) -> folium.Map:
    """
    Добавление тепловой карты

    Args:
        map_obj: Объект карты Folium
        data: Список точек [(lat, lon, weight), ...]
        name: Название слоя

    Returns:
        Folium Map
    """
    heat_data = [[point[0], point[1], point[2]] for point in data]

    plugins.HeatMap(
        heat_data,
        name=name,
        min_opacity=0.2,
        radius=25,
        blur=15,
        max_zoom=13
    ).add_to(map_obj)

    return map_obj


def add_marker_cluster(
    map_obj: folium.Map,
    markers_data: List[Dict],
    name: str = "Кластер"
) -> folium.Map:
    """
    Добавление кластера маркеров

    Args:
        map_obj: Объект карты Folium
        markers_data: Список словарей с данными маркеров
                     [{'lat': ..., 'lon': ..., 'popup': ..., 'tooltip': ...}, ...]
        name: Название слоя

    Returns:
        Folium Map
    """
    marker_cluster = plugins.MarkerCluster(name=name).add_to(map_obj)

    for marker in markers_data:
        folium.Marker(
            location=[marker['lat'], marker['lon']],
            popup=marker.get('popup', ''),
            tooltip=marker.get('tooltip', ''),
            icon=folium.Icon(
                color=marker.get('color', 'blue'),
                icon=marker.get('icon', 'info-sign')
            )
        ).add_to(marker_cluster)

    return map_obj


def add_polyline(
    map_obj: folium.Map,
    coordinates: List[Tuple[float, float]],
    popup_text: Optional[str] = None,
    color: str = "blue",
    weight: int = 3,
    opacity: float = 0.8
) -> folium.Map:
    """
    Добавление линии (трек) на карту

    Args:
        map_obj: Объект карты Folium
        coordinates: Список координат [(lat, lon), ...]
        popup_text: Текст всплывающего окна
        color: Цвет линии
        weight: Толщина линии
        opacity: Прозрачность

    Returns:
        Folium Map
    """
    folium.PolyLine(
        locations=coordinates,
        popup=popup_text,
        color=color,
        weight=weight,
        opacity=opacity
    ).add_to(map_obj)

    return map_obj


def add_gps_track(
    map_obj: folium.Map,
    track_points: List[Dict],
    track_name: str,
    color: str = "blue"
) -> folium.Map:
    """
    Добавление GPS-трека с маркерами старта/финиша

    Args:
        map_obj: Объект карты Folium
        track_points: Список точек трека [{'lat': ..., 'lon': ..., 'timestamp': ...}, ...]
        track_name: Название трека
        color: Цвет трека

    Returns:
        Folium Map
    """
    if not track_points:
        return map_obj

    # Координаты для линии
    coordinates = [(point['lat'], point['lon']) for point in track_points]

    # Добавляем линию трека
    folium.PolyLine(
        locations=coordinates,
        popup=f"<b>{track_name}</b><br>Точек: {len(track_points)}",
        color=color,
        weight=3,
        opacity=0.7
    ).add_to(map_obj)

    # Маркер старта
    folium.Marker(
        location=[track_points[0]['lat'], track_points[0]['lon']],
        popup=f"<b>Старт</b><br>{track_name}<br>{track_points[0].get('timestamp', '')}",
        icon=folium.Icon(color='green', icon='play')
    ).add_to(map_obj)

    # Маркер финиша
    folium.Marker(
        location=[track_points[-1]['lat'], track_points[-1]['lon']],
        popup=f"<b>Финиш</b><br>{track_name}<br>{track_points[-1].get('timestamp', '')}",
        icon=folium.Icon(color='red', icon='stop')
    ).add_to(map_obj)

    return map_obj


def create_choropleth_map(
    center_lat: float,
    center_lon: float,
    geo_data: Dict,
    data: Dict[str, float],
    key_on: str,
    columns: List[str],
    fill_color: str = "YlGn",
    legend_name: str = "Значение"
) -> folium.Map:
    """
    Создание хороплет-карты (раскрашивание регионов по значениям)

    Args:
        center_lat: Широта центра карты
        center_lon: Долгота центра карты
        geo_data: GeoJSON данные
        data: Данные для раскрашивания
        key_on: Ключ для связывания данных
        columns: Колонки данных
        fill_color: Цветовая схема
        legend_name: Название легенды

    Returns:
        Folium Map
    """
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=10
    )

    folium.Choropleth(
        geo_data=geo_data,
        data=data,
        columns=columns,
        key_on=key_on,
        fill_color=fill_color,
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=legend_name
    ).add_to(m)

    return m


def fit_bounds_to_markers(
    map_obj: folium.Map,
    coordinates: List[Tuple[float, float]]
) -> folium.Map:
    """
    Подгонка границ карты под маркеры

    Args:
        map_obj: Объект карты Folium
        coordinates: Список координат [(lat, lon), ...]

    Returns:
        Folium Map
    """
    if coordinates:
        map_obj.fit_bounds(coordinates)

    return map_obj


def add_fullscreen_control(map_obj: folium.Map) -> folium.Map:
    """
    Добавление кнопки полноэкранного режима

    Args:
        map_obj: Объект карты Folium

    Returns:
        Folium Map
    """
    plugins.Fullscreen(
        position='topleft',
        title='Развернуть на весь экран',
        title_cancel='Выйти из полноэкранного режима',
        force_separate_button=True
    ).add_to(map_obj)

    return map_obj


def add_minimap(map_obj: folium.Map) -> folium.Map:
    """
    Добавление мини-карты

    Args:
        map_obj: Объект карты Folium

    Returns:
        Folium Map
    """
    minimap = plugins.MiniMap(toggle_display=True)
    map_obj.add_child(minimap)

    return map_obj


def add_measure_control(map_obj: folium.Map) -> folium.Map:
    """
    Добавление инструмента измерения расстояний

    Args:
        map_obj: Объект карты Folium

    Returns:
        Folium Map
    """
    plugins.MeasureControl(
        position='topleft',
        primary_length_unit='kilometers',
        secondary_length_unit='meters',
        primary_area_unit='hectares',
        secondary_area_unit='sqmeters'
    ).add_to(map_obj)

    return map_obj


def add_draw_control(map_obj: folium.Map) -> folium.Map:
    """
    Добавление инструментов рисования

    Args:
        map_obj: Объект карты Folium

    Returns:
        Folium Map
    """
    draw = plugins.Draw(
        export=True,
        draw_options={
            'polyline': True,
            'rectangle': True,
            'polygon': True,
            'circle': True,
            'marker': True,
            'circlemarker': False
        }
    )
    map_obj.add_child(draw)

    return map_obj


def add_search_control(
    map_obj: folium.Map,
    data: List[Dict],
    search_label: str = "name"
) -> folium.Map:
    """
    Добавление поиска по объектам

    Args:
        map_obj: Объект карты Folium
        data: Данные для поиска
        search_label: Поле для поиска

    Returns:
        Folium Map
    """
    from folium.plugins import Search

    # Создаем GeoJSON Feature Collection
    features = []
    for item in data:
        feature = {
            "type": "Feature",
            "properties": item,
            "geometry": {
                "type": "Point",
                "coordinates": [item.get("lon", 0), item.get("lat", 0)]
            }
        }
        features.append(feature)

    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }

    # Добавляем GeoJSON слой
    geojson_layer = folium.GeoJson(
        geojson_data,
        name="searchable_data"
    )

    # Добавляем поиск
    search = Search(
        layer=geojson_layer,
        search_label=search_label,
        placeholder='Поиск...',
        collapsed=False
    ).add_to(map_obj)

    geojson_layer.add_to(map_obj)

    return map_obj


def calculate_polygon_area(coordinates: List[Tuple[float, float]]) -> float:
    """
    Расчет площади полигона в гектарах

    Args:
        coordinates: Список координат [(lat, lon), ...]

    Returns:
        Площадь в гектарах
    """
    from math import radians, cos, sin, sqrt, atan2

    def haversine_distance(coord1, coord2):
        """Расстояние между двумя точками по формуле Гаверсинуса"""
        R = 6371000  # Радиус Земли в метрах

        lat1, lon1 = radians(coord1[0]), radians(coord1[1])
        lat2, lon2 = radians(coord2[0]), radians(coord2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    # Простой расчет площади по формуле Шнура (Shoelace formula)
    # Для более точного расчета можно использовать библиотеку geopy или shapely
    if len(coordinates) < 3:
        return 0.0

    # Конвертируем в метры и применяем формулу
    n = len(coordinates)
    area = 0.0

    for i in range(n):
        j = (i + 1) % n
        area += coordinates[i][0] * coordinates[j][1]
        area -= coordinates[j][0] * coordinates[i][1]

    area = abs(area) / 2.0

    # Приблизительный коэффициент для конвертации в метры (зависит от широты)
    avg_lat = sum(coord[0] for coord in coordinates) / n
    meters_per_degree_lat = 111320
    meters_per_degree_lon = 111320 * cos(radians(avg_lat))

    area_m2 = area * meters_per_degree_lat * meters_per_degree_lon

    # Конвертируем в гектары
    area_ha = area_m2 / 10000

    return area_ha


def export_map_to_html(map_obj: folium.Map, filename: str) -> str:
    """
    Экспорт карты в HTML файл

    Args:
        map_obj: Объект карты Folium
        filename: Имя файла

    Returns:
        Путь к сохраненному файлу
    """
    map_obj.save(filename)
    return filename
