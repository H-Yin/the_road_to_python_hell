import math

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from PIL import Image
from matplotlib.lines import Line2D
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import Wedge


class PolarHistogram(object):

    def __init__(self, start_angle: int = 90, inner_padding: float = None, bg_color="#F8F1F1"):
        self.start_angle = start_angle  # 起始角度，默认是 90 度, 即 x 轴正方向
        self.angle_size = 350  # 从起始角度到结束角度之间的大小，默认留 10 度用于标记参考线；
        self.inner_padding = inner_padding  # 楔子开始绘制的地方离坐标原点的距离，用于填充文字（标题等）；
        self.bg_color = bg_color
        self.wedge_size = None  # 每个楔子的大小 = angle_size / 楔子数
        self.wedge_padding = None  # 楔子之间的填充
        self.limit_size = None  # 坐标轴的限制
        self.ax = None  # 子图

    @staticmethod
    def get_coordinate(angle, radius, padding: float = None):
        length = radius + (padding if padding else 0.0)
        radian = math.radians(angle)
        return length * math.cos(radian), length * math.sin(radian)

    @staticmethod
    def get_chord_length(angle, radius):
        return 2 * radius * math.sin(math.radians(angle) / 2)

    def draw_wedge(self, start_angle, end_angle, radius, width, color):
        wedge = Wedge((0, 0), radius, start_angle, end_angle, width=width, color=color)
        self.ax.add_artist(wedge)

    def draw_image(self, x, y, image_path: str, rotation, zoom=1):
        try:
            flag = Image.open(image_path)
            flag = flag.rotate(rotation if rotation > 270 else rotation - 180)
            im = OffsetImage(flag, zoom=zoom, interpolation="lanczos", resample=True, visible=True)
            self.ax.add_artist(AnnotationBbox(im, (x, y), frameon=False, xycoords="data"))
        except FileNotFoundError:
            print(image_path)

    def draw_label(self, x, y, angle, label, value=None, fontsize=18):
        angle = angle % 360
        if 90 < angle < 270:
            text = "{} ({})".format(label, value) if value else label
            self.ax.text(x, y, text, fontsize=fontsize, rotation=angle - 180, ha="right", va="center",
                         rotation_mode="anchor")
        else:
            text = "({}) {}".format(value, label) if value else label
            self.ax.text(x, y, text, fontsize=fontsize, rotation=angle, ha="left", va="center",
                         rotation_mode="anchor")

    def draw_wedges(self, *data):
        for index, data in enumerate(zip(*data)):
            data = list(data) + ([None, None])
            value, label, color, label_image = data[:4]
            start_angle = self.start_angle + index * self.wedge_size + self.wedge_padding
            end_angle = self.start_angle + (index + 1) * self.wedge_size
            label_angle = (start_angle + end_angle) / 2
            radis = self.inner_padding + value

            self.draw_wedge(start_angle, end_angle, radis, value, color)
            image_size = self.get_chord_length(self.wedge_size, radis)
            if label_image is not None:
                image_x, image_y = self.get_coordinate(label_angle, radis, image_size * 0.8)
                self.draw_image(image_x, image_y, label_image, label_angle, image_size / 2)
                text_x, text_y = self.get_coordinate(label_angle, radis, image_size * 1.6)
            else:
                text_x, text_y = self.get_coordinate(label_angle, radis, image_size / 2)
            self.draw_label(text_x, text_y, label_angle, label, value)

    def draw_reference_lines(self, values, width: float = 0.01, fontsize=18):
        for value in values:
            radis = self.inner_padding + value
            self.draw_wedge(0, 360, radis, width, self.bg_color)
            x, y = self.get_coordinate(self.start_angle + self.angle_size, radis)
            pad_x, pad_y = self.get_coordinate(self.start_angle + 90, 0.2)
            self.ax.text(x + pad_x, y + pad_y, value, ha="center", va="center", rotation=self.angle_size - 360,
                         rotation_mode="anchor", fontsize=fontsize)

    def draw_legends(self, labels, colors, title: str = None):
        lines = [
            Line2D([], [], marker='s', markersize=24, linewidth=0, color=c)
            for c in colors
        ]

        self.ax.legend(lines, labels, title=title, title_fontsize=28, fontsize=24,
                       loc="upper left", alignment="left")

    def draw_title(self, text):
        self.ax.text(0, 0, text, va="center", ha="center", fontsize=64, linespacing=1.5)

    def add_axes(self):
        sns.set_style({
            "axes.facecolor": self.bg_color,
            "figure.facecolor": self.bg_color,
            "font.family": "Times New Roman"
        })
        # 设置画布大小，坐标轴可视范围，坐标轴位置等
        fig, self.ax = plt.subplots(nrows=1, ncols=1, figsize=(30, 30))
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.ax.set(xlim=(-self.limit_size, self.limit_size), ylim=(-self.limit_size, self.limit_size))

        self.ax.spines['top'].set_color('none')
        self.ax.spines['right'].set_color('none')
        self.ax.xaxis.set_ticks_position('bottom')
        self.ax.spines['bottom'].set_position(('data', 0))
        self.ax.yaxis.set_ticks_position('left')
        self.ax.spines['left'].set_position(('data', 0))

    def draw(self, *data, reference_values: list = None, legend_data: dict = None):
        values = data[0]
        # settings
        self.wedge_size = self.angle_size / len(df)
        self.wedge_padding = self.wedge_size * 0.1  # 楔子之间的填充间隔
        self.inner_padding = min(values) * 2 if self.inner_padding is None else self.inner_padding
        self.limit_size = (max(values) + self.inner_padding) * 1.25
        # 建画布
        self.add_axes()
        # 计算每个楔子的位置，并画出每个楔子
        self.draw_wedges(*data)
        # 画参考线
        self.draw_reference_lines(reference_values)
        # 画提示
        if len(data) >= 3 and legend_data is not None:
            self.draw_legends(
                labels=legend_data["labels"],
                colors=legend_data["colors"],
                title=legend_data["title"] if "title" in legend_data else ""
            )
        # 画标题
        self.draw_title(text="World Happiness Report 2023".replace(" ", "\n"))

        plt.axis("off")
        plt.tight_layout()

    def plot(self, *data, reference_values: list = None, legend_data: dict = None):
        self.draw(*data, reference_values=reference_values, legend_data=legend_data)
        plt.show()

    def save(self, *data, image_file="test.png", reference_values: list = None, legend_data: dict = None):
        self.draw(*data, reference_values=reference_values, legend_data=legend_data)
        plt.savefig(image_file)


if __name__ == "__main__":
    df = pd.read_excel("data/merged_data.xlsx")
    df = df.sort_values(by="score", ascending=True).reset_index(drop=True)

    color_dict = {
        "High income": "#468FA8",
        "Upper middle income": "#62466B",
        "Lower middle income": "#E5625E",
        "Low income": "#6B0F1A",
        "Unknown": "#909090"
    }

    legend_dict = {
        "labels": ["High income", "Upper middle income", "Lower middle income", "Low income", "Unknown"],
        "colors": ["#468FA8", "#62466B", "#E5625E", "#6B0F1A", "#909090"],
        "title": "Income level according to the World Bank"
    }

    df["color"] = df["income"].apply(lambda x: color_dict[x])
    df["image_path"] = df["country"].apply(
        lambda country: "data/flags/{}.png".format(country.lower().replace(" ", "_"))
    )

    ph = PolarHistogram()
    # ph.plot(df["score"], df["country"])
    # ph.plot(df["score"], df["country"], df["color"])
    ph.plot(df["score"], df["country"], df["color"], df["image_path"],
            reference_values=[2.0, 4.0, 6.0], legend_data=legend_dict
            )
