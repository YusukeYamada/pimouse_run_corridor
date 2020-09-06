#!/usr/bin/env python  #wall_around.pyの形式で実行できるようにするためのもの
import rospy,copy,math　#Python用のROSの基本ライブラリのrospyをmathをコピーして読み込む文のこと
from geometry_msgs.msg import Twist　#geometry_msgsパッケージの下のmsgパッケージからTwist型を読み込む
from std_srvs.srv import Trigger, TriggerResponse　#std_srvsパッケージの下のsrvパッケージからTriggerRseponseを読み込む
from pimouse_ros.msg import LightSensorValues　#pimouse_rosパッケージの下のmsgパッケージからLightSensorValuesを読み込む

class WallAround():　#WallAroundというクラスを定義
    def __init__(self):　#__init__という関数でこれがコンストラクタ(クラスのオブジェクトを作成するときに初期化を行うための関数)となる
        self.cmd_vel = rospy.Publisher('/cmd_vel',Twist,queue_size=1)　#ノードがマスターに対してcmd_velのメッセージでトピック'/cmd_velを配信する宣言

        self.sensor_values = LightSensorValues()　#sensor_valuesのメッセージでトピックLightsSensorValuesを配信する
        rospy.Subscriber('/lightsensors', LightSensorValues, self.callback) #トピック'/lightsensorsを受信するとcallback関数を実行

    def callback(self,messages):　#指定したトピックであるlightsensorsを受信するたびにcallbackを実行
        self.sensor_values = messages　#メッセージはセンサーの値で配信

    def wall_front(self,ls):
        
        return ls.left_forward > 50 or ls.right_forward > 50

    def too_right(self,ls):
        return ls.right_side > 50

    def too_left(self,ls):
        return ls.left_side > 50

    def run(self):
        rate = rospy.Rate(20)
        data = Twist()

        data.linear.x = 0.3
        data.angular.z = 0.0
        while not rospy.is_shutdown():
            if self.wall_front(self.sensor_values):
                data.angular.z = - math.pi
            elif self.too_right(self.sensor_values):
                data.angular.z = math.pi
            elif self.too_left(self.sensor_values):
                data.angular.z = -math.pi

            else:
                e = 50 - self.sensor_values.left_side
                data.angular.z = e * math.pi / 180.0

            self.cmd_vel.publish(data)
            rate.sleep()

if __name__ == '__main__':
    rospy.init_node('wall_stop')
    rospy.wait_for_service('/motor_on')
    rospy.wait_for_service('/motor_off')
    rospy.on_shutdown(rospy.ServiceProxy('/motor_off',Trigger).call)
    rospy.ServiceProxy('/motor_on',Trigger).call()
    WallAround().run()
