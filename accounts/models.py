from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db.models.signals import post_save #model.save()が呼ばれた後に発火するシグナル
from django.dispatch import receiver
from hashids import Hashids

#カスタムユーザーマネージャークラス
class UserManager(BaseUserManager):
    #メールアドレスの検証
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('メールアドレスは必須です')
        #メールアドレスの正規化
        email = self.normalize_email(email)
        email = email.lower()
        
        #ユーザーオブジェクトの作成と保存
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    #スーパーユーザーの作成
    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email, password,**extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        
        return user
    
#カスタムユーザーモデル
class UserAccount(AbstractBaseUser, PermissionsMixin):
    uid = models.CharField("uid", max_length=30, unique=True)
    email = models.EmailField("メールアドレス",max_length=255, unique=True)
    name = models.CharField("名前", max_length=255)
    avatar = models.ImageField(upload_to="avatar", verbose_name="プロフィール画像",null=True, blank=True)
    introduction = models.TextField("自己紹介", null=True, blank=True)
    updated_at = models.DateTimeField("更新日", auto_now=True)
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    
    #アクティブ状態とスタッフ権限フィールド
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    #ユーザーマネージャーと認証フィールドの設定
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        verbose_name = "ユーザーアカウント"
        verbose_name_plural = "ユーザーアカウント"
    
    def __str__(self):
        return self.name
    
@receiver(post_save, sender=UserAccount) #特定のシグナルを受け取った際に実行される関数を登録
def create_random_user_uid(sender, instance,created, **kwargs):
    # 新規作成時にランダムUIDを作成
    if created:
        hashids = Hashids(salt="xRXSMT8XpzdUbDNM9qkv6JzUezU64D4Z", min_length=8)
        instance.uid = hashids.encode(instance.id)
        instance.save()
        
class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    sport_name = models.CharField("競技名", max_length=50)
    game_date = models.DateTimeField("試合日")
    release_date = models.DateTimeField("発売日")
    opponent_team = models.CharField("対戦相手", max_length=100)
    place = models.CharField("会場", max_length=100)
    
    def __str__(self):
        return f"{self.sport_name} vs {self.opponent_team} on {self.game_date.strftime('%Y-%m-%d')} at {self.place}"
    class Meta:
        ordering = ['-game_date']  # 試合日が新しい順に表示
        verbose_name = "Event"
        verbose_name_plural = "Events"
        unique_together = ('sport_name', 'game_date', 'opponent_team')
        
class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ('筑波大生', '筑波大生'),
        ('筑波大教職員', '筑波大教職員'),
        ('つくば市在住', 'つくば市在住'),
        ('つくば市在勤', 'つくば市在勤'),
        ('卒業生', '卒業生'),
        ('その他', 'その他')
    ]
    AGE_GROUP_CHOICES = [
        ('18歳以下', '18歳以下'),
        ('19&20代', '19&20代'),
        ('30代', '30代'),
        ('40代', '40代'),
        ('50代', '50代'),
        ('60代', '60代'),
        ('70代以上', '70代以上')
    ]
    PLAY_FREQ_CHOICES = [
        ('3回+/週', '3回+/週'),
        ('1~2回/週', '1~2回/週'),
        ('1回/月', '1回/月'),
        ('1回/2~3カ月', '1回/2~3カ月'),
        ('1回-/2~3カ月','1回-/2~3カ月')
    ]
    VIEWING_FREQ_CHOICES = [
        ('3+回/週', '3+回/週'),
        ('1~2回/週', '1~2回/週'),
        ('24~36回/年', '24~36回/年'),
        ('12回/年', '12回/年'),
        ('4~6回/年', '4~6回/年'),
        ('2回/年', '2回/年'),
        ('1回/年', '1回/年'),
        ('1-回/年', '1-回/年'),
    ]
    SPECIAL_VIEWING_CHOICES = [
        ('3+回/週', '3+/週'),
        ('1~2回/週', '1~2回/週'),
        ('24~36回/年', '24~36回/年'),
        ('12回/年', '12回/年'),
        ('4~6回/年', '4~6回/年'),
        ('2回/年', '2回/年'),
        ('1回/年', '1回/年'),
        ('1-回/年', '1-回/年'),
    ]
    DEPARTMENT_CHOICES = [
        ("筑波大生でない", "筑波大生でない"),
        ("人文・文化学群", "人文・文化学群"),
        ("社会・国際学群", "社会・国際学群"),
        ("人間学群", "人間学群"),
        ("生命環境学群", "生命環境学群"),
        ("理工学群", "理工学群"),
        ("情報学群", "情報学群"),
        ("医学群", "医学群"),
        ("体育専門学群", "体育専門学群"),
        ("芸術専門学群", "芸術専門学群"),
        ("総合学域群", "総合学域群"),
        ("人文社会ビジネス科学学術院", "人文社会ビジネス科学学術院"),
        ("理工情報生命学術院", "理工情報生命学術院"),
        ("人間総合科学学術院", "人間総合科学学術院"),
        ("グローバル教育院", "グローバル教育院")
    ]
    ATTENDANCE_COUNT_CHOICES = [
        ('0', '0'),
        ('1~2', '1~2'),
        ('3~4', '3~4'),
        ('5~6', '5~6'),
        ('7~', '7~'),
    ]
    SCHOOL_YEAR_CHOICES = [
        ('1年', '1年'),
        ('2年', '2年'),
        ('3年', '3年'),
        ('4年', '4年'),
        ('Master', 'Master'),
        ('Ph.D', 'Ph.D'),
        ('他大生', '他大生'),
        ('筑波大生でない', '筑波大生でない'),
    ]
    GENDER_CHOICES = [
        ('男性', '男性'),
        ('女性', '女性'),
        ('その他', 'その他'),
        ('無回答', '無回答')
    ]
    ticket_id = models.AutoField(primary_key=True)
    quantity = models.PositiveIntegerField("購入枚数")
    purchase_datetime = models.DateTimeField("購入日時")
    ticket_type = models.CharField("チケット種類", max_length=50)
    ticket_price = models.PositiveIntegerField("チケット価格")
    seat_type = models.CharField("座席種", max_length=50)
    coupon_applied = models.BooleanField("クーポン有無", default=False)
    category = models.CharField("カテゴリー", max_length=50, choices=CATEGORY_CHOICES)
    nationality = models.CharField("国籍", max_length=50)
    gender = models.CharField("性別", max_length=50, choices=GENDER_CHOICES)
    age_group = models.CharField("年代", max_length=50, choices=AGE_GROUP_CHOICES)
    school_year = models.CharField("学年", max_length=50, choices=SCHOOL_YEAR_CHOICES)
    department = models.CharField("所属", max_length=50, choices=DEPARTMENT_CHOICES)
    referral_source = models.CharField("流入経路", max_length=50)
    attendance_count = models.CharField("来場回数", max_length=50, choices=ATTENDANCE_COUNT_CHOICES)
    play_freq = models.CharField("スポーツ実施頻度", max_length=50, choices=PLAY_FREQ_CHOICES)
    viewing_freq = models.CharField("スポーツ観戦観戦頻度", max_length=50, choices=VIEWING_FREQ_CHOICES)
    special_viewing = models.CharField("開催競技観戦頻度", max_length=50, choices=SPECIAL_VIEWING_CHOICES)
    event_id = models.ForeignKey(Event, on_delete=models.PROTECT)