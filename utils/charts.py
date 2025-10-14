"""
Charts - Утилиты для создания графиков
"""
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Optional, Tuple
import pandas as pd


def create_pie_chart(
    values: List[float],
    names: List[str],
    title: str,
    colors: Optional[List[str]] = None,
    hole: float = 0
) -> go.Figure:
    """
    Создание круговой диаграммы

    Args:
        values: Значения
        names: Названия
        title: Заголовок
        colors: Цвета (опционально)
        hole: Размер отверстия для donut chart (0-0.9)

    Returns:
        Plotly Figure
    """
    fig = px.pie(
        values=values,
        names=names,
        title=title,
        color_discrete_sequence=colors,
        hole=hole
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Значение: %{value}<br>Доля: %{percent}<extra></extra>'
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        )
    )

    return fig


def create_bar_chart(
    x: List,
    y: List[float],
    title: str,
    x_label: str = "",
    y_label: str = "",
    color: Optional[str] = None,
    colors: Optional[List[str]] = None,
    orientation: str = 'v'
) -> go.Figure:
    """
    Создание столбчатой диаграммы

    Args:
        x: Значения по оси X
        y: Значения по оси Y
        title: Заголовок
        x_label: Подпись оси X
        y_label: Подпись оси Y
        color: Единый цвет
        colors: Цвета для каждого столбца
        orientation: 'v' (вертикальная) или 'h' (горизонтальная)

    Returns:
        Plotly Figure
    """
    if orientation == 'v':
        fig = go.Figure(data=[
            go.Bar(x=x, y=y, marker_color=colors if colors else color)
        ])
    else:
        fig = go.Figure(data=[
            go.Bar(x=y, y=x, marker_color=colors if colors else color, orientation='h')
        ])

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        hovermode='x unified'
    )

    return fig


def create_grouped_bar_chart(
    categories: List[str],
    data: Dict[str, List[float]],
    title: str,
    x_label: str = "",
    y_label: str = ""
) -> go.Figure:
    """
    Создание сгруппированной столбчатой диаграммы

    Args:
        categories: Категории (ось X)
        data: Словарь {название_серии: [значения]}
        title: Заголовок
        x_label: Подпись оси X
        y_label: Подпись оси Y

    Returns:
        Plotly Figure
    """
    fig = go.Figure()

    for series_name, values in data.items():
        fig.add_trace(go.Bar(
            name=series_name,
            x=categories,
            y=values
        ))

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        barmode='group',
        hovermode='x unified'
    )

    return fig


def create_line_chart(
    x: List,
    y: List[float],
    title: str,
    x_label: str = "",
    y_label: str = "",
    line_name: str = "Значение",
    color: str = "#1f77b4"
) -> go.Figure:
    """
    Создание линейного графика

    Args:
        x: Значения по оси X
        y: Значения по оси Y
        title: Заголовок
        x_label: Подпись оси X
        y_label: Подпись оси Y
        line_name: Название линии
        color: Цвет линии

    Returns:
        Plotly Figure
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='lines+markers',
        name=line_name,
        line=dict(color=color, width=2),
        marker=dict(size=6)
    ))

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        hovermode='x unified'
    )

    return fig


def create_multiline_chart(
    x: List,
    data: Dict[str, List[float]],
    title: str,
    x_label: str = "",
    y_label: str = ""
) -> go.Figure:
    """
    Создание графика с несколькими линиями

    Args:
        x: Значения по оси X
        data: Словарь {название_линии: [значения]}
        title: Заголовок
        x_label: Подпись оси X
        y_label: Подпись оси Y

    Returns:
        Plotly Figure
    """
    fig = go.Figure()

    for line_name, y_values in data.items():
        fig.add_trace(go.Scatter(
            x=x,
            y=y_values,
            mode='lines+markers',
            name=line_name,
            line=dict(width=2),
            marker=dict(size=6)
        ))

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        hovermode='x unified'
    )

    return fig


def create_scatter_chart(
    x: List[float],
    y: List[float],
    title: str,
    x_label: str = "",
    y_label: str = "",
    point_labels: Optional[List[str]] = None,
    color_values: Optional[List[float]] = None,
    size_values: Optional[List[float]] = None
) -> go.Figure:
    """
    Создание точечного графика

    Args:
        x: Значения по оси X
        y: Значения по оси Y
        title: Заголовок
        x_label: Подпись оси X
        y_label: Подпись оси Y
        point_labels: Подписи точек
        color_values: Значения для цвета точек
        size_values: Значения для размера точек

    Returns:
        Plotly Figure
    """
    marker_config = {}

    if color_values:
        marker_config['color'] = color_values
        marker_config['colorscale'] = 'Viridis'
        marker_config['showscale'] = True

    if size_values:
        marker_config['size'] = size_values
        marker_config['sizemode'] = 'diameter'
        marker_config['sizeref'] = 2. * max(size_values) / (40. ** 2) if size_values else 1
    else:
        marker_config['size'] = 10

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='markers',
        text=point_labels,
        marker=marker_config,
        hovertemplate='<b>%{text}</b><br>X: %{x}<br>Y: %{y}<extra></extra>' if point_labels else None
    ))

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label
    )

    return fig


def create_heatmap(
    z_values: List[List[float]],
    x_labels: List[str],
    y_labels: List[str],
    title: str,
    colorscale: str = 'RdYlGn'
) -> go.Figure:
    """
    Создание тепловой карты

    Args:
        z_values: Двумерный массив значений
        x_labels: Подписи по оси X
        y_labels: Подписи по оси Y
        title: Заголовок
        colorscale: Цветовая схема

    Returns:
        Plotly Figure
    """
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_labels,
        y=y_labels,
        colorscale=colorscale,
        hovertemplate='X: %{x}<br>Y: %{y}<br>Значение: %{z}<extra></extra>'
    ))

    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title=""
    )

    return fig


def create_progress_bar_chart(
    categories: List[str],
    values: List[float],
    target: float,
    title: str
) -> go.Figure:
    """
    Создание графика прогресса

    Args:
        categories: Категории
        values: Значения (проценты)
        target: Целевое значение
        title: Заголовок

    Returns:
        Plotly Figure
    """
    # Цвета в зависимости от достижения цели
    colors = []
    for val in values:
        if val >= target:
            colors.append('#28a745')  # Зеленый
        elif val >= target * 0.7:
            colors.append('#ffc107')  # Желтый
        else:
            colors.append('#dc3545')  # Красный

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=categories,
        x=values,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{v:.1f}%" for v in values],
        textposition='outside'
    ))

    # Линия цели
    fig.add_vline(
        x=target,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Цель: {target}%",
        annotation_position="top"
    )

    fig.update_layout(
        title=title,
        xaxis_title="Процент",
        yaxis_title="",
        xaxis=dict(range=[0, 105])
    )

    return fig


def create_gauge_chart(
    value: float,
    title: str,
    max_value: float = 100,
    thresholds: Optional[Dict[str, Tuple[float, str]]] = None
) -> go.Figure:
    """
    Создание индикатора (gauge)

    Args:
        value: Текущее значение
        title: Заголовок
        max_value: Максимальное значение
        thresholds: Пороги {название: (значение, цвет)}

    Returns:
        Plotly Figure
    """
    if thresholds is None:
        thresholds = {
            'red': (max_value * 0.4, '#dc3545'),
            'yellow': (max_value * 0.7, '#ffc107'),
            'green': (max_value, '#28a745')
        }

    # Определяем цвет
    color = '#dc3545'  # По умолчанию красный
    for threshold_name, (threshold_val, threshold_color) in sorted(thresholds.items(), key=lambda x: x[1][0]):
        if value <= threshold_val:
            color = threshold_color
            break

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': title},
        delta={'reference': max_value * 0.7},
        gauge={
            'axis': {'range': [0, max_value]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, max_value * 0.4], 'color': "lightgray"},
                {'range': [max_value * 0.4, max_value * 0.7], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.7
            }
        }
    ))

    return fig


def create_stacked_bar_chart(
    categories: List[str],
    data: Dict[str, List[float]],
    title: str,
    x_label: str = "",
    y_label: str = ""
) -> go.Figure:
    """
    Создание стековой столбчатой диаграммы

    Args:
        categories: Категории (ось X)
        data: Словарь {название_серии: [значения]}
        title: Заголовок
        x_label: Подпись оси X
        y_label: Подпись оси Y

    Returns:
        Plotly Figure
    """
    fig = go.Figure()

    for series_name, values in data.items():
        fig.add_trace(go.Bar(
            name=series_name,
            x=categories,
            y=values
        ))

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        barmode='stack',
        hovermode='x unified'
    )

    return fig


def create_box_plot(
    data: Dict[str, List[float]],
    title: str,
    y_label: str = ""
) -> go.Figure:
    """
    Создание box plot (ящик с усами)

    Args:
        data: Словарь {название_группы: [значения]}
        title: Заголовок
        y_label: Подпись оси Y

    Returns:
        Plotly Figure
    """
    fig = go.Figure()

    for group_name, values in data.items():
        fig.add_trace(go.Box(
            y=values,
            name=group_name,
            boxmean='sd'  # Показывать среднее и стандартное отклонение
        ))

    fig.update_layout(
        title=title,
        yaxis_title=y_label
    )

    return fig


def create_area_chart(
    x: List,
    data: Dict[str, List[float]],
    title: str,
    x_label: str = "",
    y_label: str = "",
    stacked: bool = True
) -> go.Figure:
    """
    Создание графика с областями

    Args:
        x: Значения по оси X
        data: Словарь {название_серии: [значения]}
        title: Заголовок
        x_label: Подпись оси X
        y_label: Подпись оси Y
        stacked: Стековая область или нет

    Returns:
        Plotly Figure
    """
    fig = go.Figure()

    for series_name, y_values in data.items():
        fig.add_trace(go.Scatter(
            x=x,
            y=y_values,
            mode='lines',
            name=series_name,
            fill='tonexty' if stacked else None,
            stackgroup='one' if stacked else None
        ))

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        hovermode='x unified'
    )

    return fig


def create_histogram(
    values: List[float],
    title: str,
    x_label: str = "",
    y_label: str = "Частота",
    nbins: int = 20
) -> go.Figure:
    """
    Создание гистограммы

    Args:
        values: Значения
        title: Заголовок
        x_label: Подпись оси X
        y_label: Подпись оси Y
        nbins: Количество столбцов

    Returns:
        Plotly Figure
    """
    fig = go.Figure(data=[go.Histogram(
        x=values,
        nbinsx=nbins
    )])

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label
    )

    return fig


def add_trend_line(
    fig: go.Figure,
    x: List[float],
    y: List[float],
    name: str = "Тренд",
    color: str = "red"
) -> go.Figure:
    """
    Добавление линии тренда к существующему графику

    Args:
        fig: Plotly Figure
        x: Значения по оси X
        y: Значения по оси Y
        name: Название линии тренда
        color: Цвет линии

    Returns:
        Plotly Figure с добавленной линией тренда
    """
    # Простая линейная регрессия
    import numpy as np

    x_array = np.array(x)
    y_array = np.array(y)

    # Полиномиальная регрессия 1 степени (линейная)
    z = np.polyfit(x_array, y_array, 1)
    p = np.poly1d(z)

    fig.add_trace(go.Scatter(
        x=x,
        y=p(x_array),
        mode='lines',
        name=name,
        line=dict(color=color, dash='dash', width=2)
    ))

    return fig
