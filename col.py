from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators     import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import F
from .models import Collection, Star, Score
from Userx.models import Party, Friend, User
from press.models import Press
from Userx.utils    import UX, CTX
from .views import  Collect, STAR

class COL:
    def __init__(self, request, upk, *args, **kwargs):
        self.request = request
        self.upk =upk
        self.user = UX(self.request, upk=self.upk)

    def headline(self):
        # 获取当前用户所有好友的文章分数排名 
        # TODO :限定不同日期

        wps = [ wp.pk for wp in Press.objects.filter(author__in=self.user.friends()) ]
        HD = [wp.content_object for wp in  Score.objects.filter(object_pk__in=wps).order_by(F('score').desc()) ]
        return HD
 
    def col(self):
        # 根据不同Col 即party，把当前用户party中的用户的文章归类
        # TODO :限定不同日期
        col = {}
        for p, f in self.user.members().items():
            col[p.pk] = []
            for w in Press.objects.filter(author__in=f):
                col[p.pk].append(w)
        
        return col

    #加条广告！ 恩不好，还是写个广告模块！
class AD:
    def __init__(self, title, subtitle, content, create_time):
        self.title = title
        self.subtitle = subtitle
        self.content = content
        self.create_time = create_time


default_ad = AD('神奇的网站', '我要变成世界第一土壕了', '打败腾讯，打败百度，打败那怕些狗屁网站', '2019')

# 重写！！
@login_required
def index(request, *args, **kwargs):
    cpk = kwargs.pop('cpk', None)
    col = get_object_or_404(Party, pk=cpk) if cpk else None

    template_name = 'cs/column.html' if cpk else 'cs/index.html'
    user = get_object_or_404(User, username=request.user)
    friends = [get_object_or_404(User, username__exact=f.from_user) for f in Friend.objects.filter(to_user=request.user)]
    wps = [ wp for wp in Press.objects.filter(author__in=friends) ]
    wps_PK = [ wp.pk for wp in Press.objects.filter(author__in=friends) ]

    HD = [wp.content_object for wp in  Score.objects.filter(object_pk__in=wps_PK).order_by(F('score').desc())]
    print(HD, Score.objects.filter(object_pk__in=wps_PK))

    context = {
        'headline': HD[0] if HD else default_ad,
        'neckline_1': HD[1] if len(HD)>1 else default_ad,
        'neckline_2': HD[2] if len(HD)>2 else default_ad,
        'cols': Party.objects.filter(leader__exact=user),
        'user':user,
        'wps': wps,
    }
    context.update(CTX)
    return render(request, template_name, context)
