# 可视化风格使用指南

本文档展示如何在其他项目中复用这套可视化风格配置。

## 📁 文件说明

- `visualization_style.yaml`: 可视化风格配置文件
- `visualization_utils.py`: 可视化工具类
- `visualization_usage_examples.md`: 使用示例（本文档）

## 🚀 快速开始

### 1. 复制配置文件到您的项目

```bash
# 复制配置文件
cp config/visualization_style.yaml /path/to/your/project/
cp config/visualization_utils.py /path/to/your/project/
```

### 2. 基本使用

```python
from visualization_utils import VisualizationManager
import numpy as np
import pandas as pd

# 初始化可视化管理器
viz = VisualizationManager("visualization_style.yaml")

# 创建示例数据
np.random.seed(42)
x = np.random.randn(100)
y = 2 * x + np.random.randn(100) * 0.5

# 创建散点图
viz.create_scatter_plot(
    x_data=x, 
    y_data=y,
    output_path="my_scatter_plot.png",
    title="My Data Correlation",
    xlabel="Feature X",
    ylabel="Feature Y"
)
```

## 📊 具体使用示例

### 散点图 (Scatter Plot)

```python
# 简单散点图
viz.create_scatter_plot(
    x_data=x_values,
    y_data=y_values,
    output_path="correlation_plot.png",
    title="Feature Correlation Analysis",
    xlabel="Independent Variable",
    ylabel="Dependent Variable",
    add_trend_line=True
)

# 分组散点图
groups = np.array(['group1', 'group2', 'group1', 'group2', ...])
group_names = ['group1', 'group2']

viz.create_scatter_plot(
    x_data=x_values,
    y_data=y_values,
    groups=groups,
    group_names=group_names,
    output_path="grouped_scatter.png",
    title="Grouped Analysis",
    xlabel="X Variable",
    ylabel="Y Variable"
)
```

### 箱线图 (Box Plot)

```python
# 准备数据
data = pd.DataFrame({
    'strategy': ['A', 'B', 'C'] * 30,
    'performance': np.random.randn(90)
})

# 创建箱线图
viz.create_box_plot(
    data=data,
    x_col='strategy',
    y_col='performance',
    output_path="strategy_comparison.png",
    title="Strategy Performance Comparison",
    xlabel="Strategy Type",
    ylabel="Performance Score"
)
```

### 热图 (Heatmap)

```python
# 准备相关性矩阵
correlation_matrix = pd.DataFrame({
    'Feature1': [1.0, 0.8, 0.3],
    'Feature2': [0.8, 1.0, 0.5],
    'Feature3': [0.3, 0.5, 1.0]
}, index=['Feature1', 'Feature2', 'Feature3'])

# 创建热图
viz.create_heatmap(
    data=correlation_matrix,
    output_path="correlation_heatmap.png",
    title="Feature Correlation Matrix"
)
```

### 直方图 (Histogram)

```python
# 简单直方图
viz.create_histogram(
    data=np.random.randn(1000),
    output_path="distribution.png",
    title="Data Distribution",
    xlabel="Value",
    ylabel="Frequency"
)

# 分组直方图
data = np.random.randn(300)
groups = np.array(['A', 'B', 'C'] * 100)
group_names = ['A', 'B', 'C']

viz.create_histogram(
    data=data,
    groups=groups,
    group_names=group_names,
    output_path="grouped_histogram.png",
    title="Distribution by Group",
    xlabel="Value",
    ylabel="Frequency"
)
```

## 🎨 自定义配置

### 修改颜色方案

```yaml
# 在visualization_style.yaml中修改
colors:
  strategy_colors:
    my_group1: "#FF6B6B"    # 红色
    my_group2: "#4ECDC4"    # 青色
    my_group3: "#45B7D1"    # 蓝色
    my_group4: "#96CEB4"    # 绿色
```

### 调整图表尺寸

```yaml
# 修改默认图表尺寸
global_settings:
  figure_size: [12, 9]      # [宽, 高]
  dpi: 300                  # 分辨率

# 或为特定图表类型设置
chart_types:
  correlation_scatter:
    figure_size: [14, 10]
```

### 自定义字体大小

```yaml
font_sizes:
  title: 18                 # 主标题
  axis_label: 16            # 坐标轴标签
  tick_label: 14            # 刻度标签
  legend: 14                # 图例
```

## 🔧 便捷函数

对于简单的绘图需求，可以使用便捷函数：

```python
from visualization_utils import quick_scatter, quick_boxplot, quick_heatmap

# 快速散点图
quick_scatter(x_data, y_data, "quick_scatter.png", 
              title="Quick Analysis", xlabel="X", ylabel="Y")

# 快速箱线图
quick_boxplot(data, 'category', 'value', "quick_box.png",
              title="Quick Comparison")

# 快速热图
quick_heatmap(correlation_df, "quick_heatmap.png",
              title="Quick Correlation")
```

## 🎯 实际项目集成示例

### 在机器学习项目中使用

```python
# ml_visualization.py
from visualization_utils import VisualizationManager
import pandas as pd
import numpy as np

class MLVisualizationHelper:
    def __init__(self, config_path="visualization_style.yaml"):
        self.viz = VisualizationManager(config_path)
    
    def plot_feature_correlation(self, X, feature_names, output_dir="plots/"):
        """绘制特征相关性热图"""
        corr_matrix = pd.DataFrame(X, columns=feature_names).corr()
        self.viz.create_heatmap(
            data=corr_matrix,
            output_path=f"{output_dir}/feature_correlation.png",
            title="Feature Correlation Matrix"
        )
    
    def plot_model_comparison(self, results_df, output_dir="plots/"):
        """绘制模型性能对比"""
        self.viz.create_box_plot(
            data=results_df,
            x_col='model',
            y_col='accuracy',
            output_path=f"{output_dir}/model_comparison.png",
            title="Model Performance Comparison",
            xlabel="Model Type",
            ylabel="Accuracy Score"
        )
    
    def plot_prediction_vs_actual(self, y_true, y_pred, output_dir="plots/"):
        """绘制预测值vs实际值散点图"""
        self.viz.create_scatter_plot(
            x_data=y_true,
            y_data=y_pred,
            output_path=f"{output_dir}/prediction_vs_actual.png",
            title="Prediction vs Actual Values",
            xlabel="Actual Values",
            ylabel="Predicted Values",
            add_trend_line=True
        )

# 使用示例
ml_viz = MLVisualizationHelper()
ml_viz.plot_feature_correlation(X_train, feature_names)
ml_viz.plot_model_comparison(results_df)
ml_viz.plot_prediction_vs_actual(y_test, y_pred)
```

### 在数据分析项目中使用

```python
# data_analysis_viz.py
from visualization_utils import VisualizationManager

class DataAnalysisViz:
    def __init__(self):
        self.viz = VisualizationManager()
    
    def create_dashboard(self, data, output_dir="dashboard/"):
        """创建数据分析仪表板"""
        
        # 1. 数据分布
        for column in data.select_dtypes(include=[np.number]).columns:
            self.viz.create_histogram(
                data=data[column].values,
                output_path=f"{output_dir}/{column}_distribution.png",
                title=f"{column.title()} Distribution",
                xlabel=column.title(),
                ylabel="Frequency"
            )
        
        # 2. 相关性分析
        numeric_data = data.select_dtypes(include=[np.number])
        if len(numeric_data.columns) > 1:
            corr_matrix = numeric_data.corr()
            self.viz.create_heatmap(
                data=corr_matrix,
                output_path=f"{output_dir}/correlation_matrix.png",
                title="Variable Correlation Matrix"
            )
        
        # 3. 分组对比
        if 'category' in data.columns:
            for numeric_col in numeric_data.columns:
                self.viz.create_box_plot(
                    data=data,
                    x_col='category',
                    y_col=numeric_col,
                    output_path=f"{output_dir}/{numeric_col}_by_category.png",
                    title=f"{numeric_col.title()} by Category",
                    xlabel="Category",
                    ylabel=numeric_col.title()
                )

# 使用示例
analyzer = DataAnalysisViz()
analyzer.create_dashboard(your_dataframe)
```

## 📋 配置文件详解

### 全局设置
- `style`: seaborn样式 (whitegrid, darkgrid, white, dark, ticks)
- `font_family`: 字体族
- `figure_size`: 默认图表尺寸
- `dpi`: 图片分辨率
- `alpha`: 默认透明度

### 颜色配置
- `strategy_colors`: 分组颜色映射
- `heatmap_colormap`: 热图颜色映射
- `trend_line`: 趋势线颜色

### 图表特定配置
- `scatter_plot`: 散点图配置
- `box_plot`: 箱线图配置
- `heatmap`: 热图配置
- `histogram`: 直方图配置

## 💡 最佳实践

1. **保持一致性**: 在同一项目中使用相同的配置文件
2. **适度自定义**: 根据项目需求调整颜色和尺寸
3. **文档化**: 记录您的自定义配置
4. **版本控制**: 将配置文件纳入版本控制
5. **测试**: 在不同数据集上测试可视化效果

## 🔍 故障排除

### 常见问题

1. **字体问题**: 如果字体显示异常，检查系统是否安装了DejaVu Sans字体
2. **颜色不匹配**: 确保分组名称与配置文件中的颜色映射一致
3. **图片保存失败**: 检查输出目录是否存在且有写入权限

### 调试技巧

```python
# 打印当前配置
viz = VisualizationManager()
print("Current colors:", viz.get_colors())
print("Current config:", viz.config)

# 测试基本功能
import numpy as np
x = np.random.randn(50)
y = x + np.random.randn(50) * 0.1
viz.create_scatter_plot(x, y, "test_plot.png")
```

## 📚 扩展阅读

- [Matplotlib官方文档](https://matplotlib.org/stable/contents.html)
- [Seaborn官方文档](https://seaborn.pydata.org/)
- [数据可视化最佳实践](https://www.data-to-viz.com/)

---

**提示**: 这套可视化配置基于AlphaFold3 iPAE分析项目开发，经过实际验证，适用于科学数据可视化场景。
