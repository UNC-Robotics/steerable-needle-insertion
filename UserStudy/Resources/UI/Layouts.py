"""Layouts defined as functions"""
 
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



VIEW_MAP = {'': [None, 0],
            'Two Top Three Bottom': [TWO_TOP_THREE_BOTTOM, 5],
            'Three Top Two Bottom': [THREE_TOP_TWO_BOTTOM, 5],
            }