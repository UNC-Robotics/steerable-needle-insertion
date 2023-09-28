import numpy as np

"""Layouts defined as functions"""

def SINGLE(inputText):
    return f"""
            <layout type="horizontal">
                <item>
                    <view class="vtkMRMLViewNode" singletontag="{inputText[0]}">
                        <property name="viewlabel" action="default">{inputText[0]}</property>
                    </view>
                </item>
            </layout>
            """

def TWO_VERTICAL(inputText):
    return f"""
            <layout type="vertical" split="true">
                <item splitSize="500">
                    <view class="vtkMRMLViewNode" singletontag="{inputText[0]}">
                        <property name="viewlabel" action="default">{inputText[0]}</property>
                    </view>
                </item>
                <item splitSize="500">
                    <view class="vtkMRMLViewNode" singletontag="{inputText[1]}">
                        <property name="viewlabel" action="default">{inputText[1]}</property>
                    </view>
                </item>
            </layout>
            """

def TWO_HORIZONTAL(inputText):
    return f"""
            <layout type="horizontal" split="true">
                <item splitSize="500">
                    <view class="vtkMRMLViewNode" singletontag="{inputText[0]}">
                        <property name="viewlabel" action="default">{inputText[0]}</property>
                    </view>
                </item>
                <item splitSize="500">
                    <view class="vtkMRMLViewNode" singletontag="{inputText[1]}">
                        <property name="viewlabel" action="default">{inputText[1]}</property>
                    </view>
                </item>
            </layout>
            """

def ONE_TOP_TWO_BOTTOM(inputText):
    return f"""
            <layout type="vertical"  split="true">
                <item splitSize="500">
                    <view class="vtkMRMLViewNode" singletontag="{inputText[0]}">
                        <property name="viewlabel" action="default">{inputText[0]}</property>
                    </view>
                </item>
                <item splitSize="500">
                    <layout type="horizontal">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[1]}" type="secondary">
                                <property name="viewlabel" action="default">{inputText[1]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[2]}" type="endoscopy">
                                <property name="viewlabel" action="default">{inputText[2]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
            </layout>
            """

def TWO_TOP_ONE_BOTTOM(inputText):
    return f"""
            <layout type="vertical"  split="true">
                <item splitSize="500">
                    <layout type="horizontal">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[0]}">
                                <property name="viewlabel" action="default">{inputText[0]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[1]}" type="secondary">
                                <property name="viewlabel" action="default">{inputText[1]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
                <item splitSize="500">
                    <view class="vtkMRMLViewNode" singletontag="{inputText[2]}">
                        <property name="viewlabel" action="default">{inputText[2]}</property>
                    </view>
                </item>
            </layout>
            """

def ONE_LEFT_TWO_RIGHT(inputText):
    return f"""
            <layout type="horizontal">
                <item>
                    <view class="vtkMRMLViewNode" singletontag="{inputText[0]}">
                        <property name="viewlabel" action="default">{inputText[0]}</property>
                    </view>
                </item>
                <item>
                    <layout type="vertical">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[1]}">
                                <property name="viewlabel" action="default">{inputText[1]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[2]}">
                                <property name="viewlabel" action="default">{inputText[2]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
            </layout>
            """

def TWO_LEFT_ONE_RIGHT(inputText):
    return f"""
            <layout type="horizontal">
                <item>
                    <layout type="vertical">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[0]}">
                            <property name="viewlabel" action="default">{inputText[0]}</property>
                        </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[1]}">
                            <property name="viewlabel" action="default">{inputText[1]}</property>
                        </view>
                        </item>
                    </layout>
                </item>
                <item>
                    <view class="vtkMRMLViewNode" singletontag="{inputText[2]}">
                    <property name="viewlabel" action="default">{inputText[2]}</property>
                    </view>
                </item>
            </layout>
            """

def FOUR_CORNERS(inputText):
    return f"""
            <layout type="vertical">
                <item>
                    <layout type="horizontal">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[0]}">
                                <property name="viewlabel" action="default">{inputText[0]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[1]}">
                                <property name="viewlabel" action="default">{inputText[1]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
                <item>
                    <layout type="horizontal">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[2]}">
                                <property name="viewlabel" action="default">{inputText[2]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[3]}">
                                <property name="viewlabel" action="default">{inputText[3]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
            </layout>
            """

def ONE_TOP_THREE_BOTTOM(inputText):
    return f"""
            <layout type="vertical" split="true">
                <item splitSize="500">
                    <view class="vtkMRMLViewNode" singletontag="{inputText[0]}">
                        <property name="viewlabel" action="default">{inputText[0]}</property>
                    </view>
                </item>
                <item splitSize="500">
                    <layout type="horizontal">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[1]}" type="secondary">
                                <property name="viewlabel" action="default">{inputText[1]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[2]}" type="endoscopy">
                                <property name="viewlabel" action="default">{inputText[2]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[3]}" type="endoscopy">
                                <property name="viewlabel" action="default">{inputText[3]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
            </layout>
            """

def THREE_TOP_ONE_BOTTOM(inputText):
    return f"""
            <layout type="vertical" split="true">
                <item splitSize="500">
                    <layout type="horizontal">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[0]}">
                                <property name="viewlabel" action="default">{inputText[0]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[1]}" type="secondary">
                                <property name="viewlabel" action="default">{inputText[1]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[2]}" type="endoscopy">
                                <property name="viewlabel" action="default">{inputText[2]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
                <item splitSize="500">
                    <view class="vtkMRMLViewNode" singletontag="{inputText[3]}" type="endoscopy">
                        <property name="viewlabel" action="default">{inputText[3]}</property>
                    </view>
                </item>
            </layout>
            """

def ONE_LEFT_THREE_RIGHT(inputText):
    return f"""
            <layout type="horizontal">
                <item>
                    <view class="vtkMRMLViewNode" singletontag="{inputText[0]}">
                        <property name="viewlabel" action="default">{inputText[0]}</property>
                    </view>
                </item>
                <item>
                    <layout type="vertical">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[1]}">
                                <property name="viewlabel" action="default">{inputText[1]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[2]}">
                                <property name="viewlabel" action="default">{inputText[2]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[3]}">
                                <property name="viewlabel" action="default">{inputText[3]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
            </layout>
            """

def THREE_LEFT_ONE_RIGHT(inputText):
    return f"""
            <layout type="horizontal">
                <item>
                    <layout type="vertical">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[0]}">
                                <property name="viewlabel" action="default">{inputText[0]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[1]}">
                                <property name="viewlabel" action="default">{inputText[1]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[2]}">
                                <property name="viewlabel" action="default">{inputText[2]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
                <item>
                    <view class="vtkMRMLViewNode" singletontag="{inputText[3]}">
                        <property name="viewlabel" action="default">{inputText[3]}</property>
                    </view>
                </item>
            </layout>
            """
 
def TWO_TOP_THREE_BOTTOM(inputText):
    return f"""
            <layout type="vertical" split="true">
                <item splitSize="500">
                    <layout type="horizontal">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[0]}">
                                <property name="viewlabel" action="default">{inputText[0]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[1]}" type="secondary">
                                <property name="viewlabel" action="default">{inputText[1]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
                <item splitSize="500">
                    <layout type="horizontal">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[2]}" type="endoscopy">
                                <property name="viewlabel" action="default">{inputText[2]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[3]}" type="secondary">
                                <property name="viewlabel" action="default">{inputText[3]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[4]}" type="endoscopy">
                                <property name="viewlabel" action="default">{inputText[4]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
            </layout>
            """

def THREE_TOP_TWO_BOTTOM(inputText):
    return f"""
            <layout type="vertical" split="true">
                <item splitSize="500">
                    <layout type="horizontal">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[0]}">
                                <property name="viewlabel" action="default">{inputText[0]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[1]}" type="secondary">
                                <property name="viewlabel" action="default">{inputText[1]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[2]}" type="endoscopy">
                                <property name="viewlabel" action="default">{inputText[2]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
                <item splitSize="500">
                    <layout type="horizontal">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[3]}" type="secondary">
                                <property name="viewlabel" action="default">{inputText[3]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[4]}" type="endoscopy">
                                <property name="viewlabel" action="default">{inputText[4]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
            </layout>
            """

def TWO_LEFT_THREE_RIGHT(inputText):
    return f"""
            <layout type="horizontal" split="true">
                <item splitSize="500">
                    <layout type="vertical">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[0]}">
                                <property name="viewlabel" action="default">{inputText[0]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[1]}" type="secondary">
                                <property name="viewlabel" action="default">{inputText[1]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
                <item splitSize="500">
                    <layout type="vertical">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[2]}" type="secondary">
                                <property name="viewlabel" action="default">{inputText[2]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[3]}" type="endoscopy">
                                <property name="viewlabel" action="default">{inputText[3]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[4]}" type="endoscopy">
                                <property name="viewlabel" action="default">{inputText[4]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
            </layout>
            """

def THREE_LEFT_TWO_RIGHT(inputText):
    return f"""
            <layout type="horizontal" split="true">
                <item splitSize="500">
                    <layout type="vertical">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[0]}">
                                <property name="viewlabel" action="default">{inputText[0]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[1]}" type="secondary">
                                <property name="viewlabel" action="default">{inputText[1]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[2]}" type="endoscopy">
                                <property name="viewlabel" action="default">{inputText[2]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
                <item splitSize="500">
                    <layout type="vertical">
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[3]}" type="secondary">
                                <property name="viewlabel" action="default">{inputText[3]}</property>
                            </view>
                        </item>
                        <item>
                            <view class="vtkMRMLViewNode" singletontag="{inputText[4]}" type="endoscopy">
                                <property name="viewlabel" action="default">{inputText[4]}</property>
                            </view>
                        </item>
                    </layout>
                </item>
            </layout>
            """

VIEW_MAP = {
            '': [None, 0],

            '(1) Single': [SINGLE, 1],

            '(2) Two Vertical': [TWO_VERTICAL, 2],
            '(2) Two Horizontal': [TWO_HORIZONTAL, 2],

            '(3) One Top Two Bottom': [ONE_TOP_TWO_BOTTOM, 3],
            '(3) Two Top One Bottom': [TWO_TOP_ONE_BOTTOM, 3],            
            '(3) One Left Two Right': [ONE_LEFT_TWO_RIGHT, 3],
            '(3) Two Left One Right': [TWO_LEFT_ONE_RIGHT, 3],

            '(4) Four Corners': [FOUR_CORNERS, 4],            
            '(4) One Top Three Bottom': [ONE_TOP_THREE_BOTTOM, 4],
            '(4) Three Top One Bottom': [THREE_TOP_ONE_BOTTOM, 4],
            '(4) One Left Three Right': [ONE_LEFT_THREE_RIGHT, 4],
            '(4) Three Left One Right': [THREE_LEFT_ONE_RIGHT, 4],

            '(5) Two Top Three Bottom': [TWO_TOP_THREE_BOTTOM, 5],
            '(5) Three Top Two Bottom': [THREE_TOP_TWO_BOTTOM, 5],
            '(5) Two Left Three Right': [TWO_LEFT_THREE_RIGHT, 5],
            '(5) Three Left Two Right': [THREE_LEFT_TWO_RIGHT, 5],
            }

def colorMap(n):
    """Returns a list [{color array}, {# colors in map}]"""
    color_map = np.array([
                          [1.000, 0.000, 0.000],
                          [1.000, 0.071, 0.000],
                          [1.000, 0.143, 0.000],
                          [1.000, 0.214, 0.000],
                          [1.000, 0.286, 0.000],
                          [1.000, 0.357, 0.000],
                          [1.000, 0.429, 0.000],
                          [1.000, 0.500, 0.000],
                          [1.000, 0.571, 0.000],
                          [1.000, 0.643, 0.000],
                          [1.000, 0.714, 0.000],
                          [1.000, 0.786, 0.000],
                          [1.000, 0.857, 0.000],
                          [1.000, 0.929, 0.000],
                          [1.000, 1.000, 0.000],
                          [0.933, 1.000, 0.000],
                          [0.867, 1.000, 0.000],
                          [0.800, 1.000, 0.000],
                          [0.733, 1.000, 0.000],
                          [0.667, 1.000, 0.000],
                          [0.600, 1.000, 0.000],
                          [0.533, 1.000, 0.000],
                          [0.467, 1.000, 0.000],
                          [0.400, 1.000, 0.000],
                          [0.333, 1.000, 0.000],
                          [0.267, 1.000, 0.000],
                          [0.200, 1.000, 0.000],
                          [0.133, 1.000, 0.000],
                          [0.067, 1.000, 0.000],
                          [0.000, 1.000, 0.000]
                         ])
    return color_map[n], color_map.shape[0]