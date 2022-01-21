//  先定义一些事先需要的变量


// 发送邮箱验证码
//  参数里的n用来判断这是发送注册验证码还是找回密码验证码
function doSendMail(obj,n) {
    var email=""
    if(n===1){
        email = $.trim($("#regname").val());
    }
    else {
        email = $.trim($("#finame").val());
    }

    if (!email.match(/.+@.+\..+/)) {
        bootbox.alert({title: "错误提示", message: "邮箱格式不正确"});
        $("#regname").focus;
        return false;
    }
    $.post("/ecode", "email=" + email+"&n="+n, function (data) {
        if (data == "eamil-invalid") {
            bootbox.alert({title: "错误提示", message: "邮箱地址格式不正确"});
            $("#regname").focus;
            return false;
        }

        if (data == "send-pass") {
            bootbox.alert({title: "信息提示", message: "邮箱已成功发送，请查收"});
            $("#regname").attr("disabled", true);// 验证码发送完成后禁止修改注册邮箱
            $(obj).attr("disabled", true); //发送邮件按钮变为不可用
            return false;
        } else {
            bootbox.alert({title: "错误提示", message: "邮箱验证码未发送成功,请联系管理员"});
            return false;
        }
    })
}

// 注册
function doRegister(e) {
    if (e != null && e.keyCode != 13) {
        return false
    }

    var regname = $.trim($("#regname").val());
    var regpass = $.trim($("#regpass").val());
    var regcode = $.trim($("#regcode").val());

    if (!regname.match(/.+@.+\..+/) || regpass.length < 5) {
        bootbox.alert({title: "错误提示", message: "注册邮箱不正确或密码小于五位"});
        return false;
    } else {
        // 构建post请求正文
        var param = "username=" + regname;
        param += "&password=" + regpass;
        param += "&ecode=" + regcode;
        // 利用jquery框架发送post请求
        $.post("/user", param, function (data) {
            if (data == "ecode-error") {
                bootbox.alert({title: "错误提示", message: "验证码错误"})
                $("#regcode").val(""); //清除验证码的值
                $("#regcode").focus(); // 让验证码框获取到焦点供用户输入
            } else if (data == "up-invalid") {
                bootbox.alert({title: "错误提示", message: "注册邮箱不正确或密码少于5位"})
            } else if (data == "reg-pass") {
                bootbox.alert({title: "信息提示", message: "恭喜你注册成功"})
                // 注册成功后 延迟二秒钟刷新当前页面
                $.get("/replyAndAddCommentCredit",function (data){
                    var regGiveCredit=data["regGiveCredit"]
                qingti("注册成功，已增加"+regGiveCredit+"积分")

    })

                setTimeout("location.reload();", 2000)
            } else if (data == "reg-fail") {
                bootbox.alert({title: "错误提示", message: "注册失败，请联系管理员"})
            }
            else if (data=="user-repeated"){
        bootbox.alert({title: "错误提示", message: "该账户已注册"})
            }
            else if (data==="ecode-timeout"){
                bootbox.alert({title: "错误提示", message: "验证码已过期"})
            }
        })
    }

}

// 找回密码
 function findPassword(e){
    if (e != null && e.keyCode != 13) {
        return false
    }

    var finame = $.trim($("#finame").val());
    var fipass = $.trim($("#fipass").val());
    var ficode = $.trim($("#ficode").val());

    if (!finame.match(/.+@.+\..+/) || fipass.length < 5) {
        bootbox.alert({title: "错误提示", message: "邮箱不正确或密码小于五位"});
        return false;
    } else {
        // 构建post请求正文
        var param = "username=" + finame;
        param += "&password=" + fipass;
        param += "&ecode=" + ficode;
        // 利用jquery框架发送post请求
        $.post("/resetUserPassword", param, function (data) {
            if(data=="no-user"){
                bootbox.alert({title: "错误提示", message: "没有找到该用户，无法重置密码"})
            }
            else if (data == "ecode-error") {
                bootbox.alert({title: "错误提示", message: "验证码错误"})
                $("#ficode").val(""); //清除验证码的值
                $("#ficode").focus(); // 让验证码框获取到焦点供用户输入
            } else if (data == "up-invalid") {
                bootbox.alert({title: "错误提示", message: "邮箱不正确或密码少于5位"})
            } else if (data == "fi-pass") {
                qingti("找回密码成功")
                setTimeout(function (){}, 1500)
                bootbox.alert({title: "信息提示", message: "重置密码成功，请重新登录",callbacks:function (){location.reload()}})
                showLogin()
            } else if (data == "fi-fail") {
                bootbox.alert({title: "错误提示", message: "找回密码失败，请联系管理员"})
            }
            else if (data==="ecode-timeout"){
                bootbox.alert({title: "错误提示", message: "验证码已过期"})
            }
        })
    }

}

// 显示登录模块
function showLogin() {

    $("#login").children("a").addClass("active");
    $("#reg").children("a").removeClass("active");
    $("#find").children("a").removeClass("active");


    $("#loginpanel").addClass("active");
    $("#regpanel").removeClass("active");
    $("#findpanel").removeClass("active");

    $("#mymodal").modal("show");
}



// 显示注册
function showReg() {
    $("#login").children("a").removeClass("active");
    $("#reg").children("a").addClass("active");
    $("#find").children("a").removeClass("active");

    $("#loginpanel").removeClass("active");
    $("#regpanel").addClass("active");
    $("#findpanel").removeClass("active");

    $("#mymodal").modal("show");
}

// 显示重置密码
function showReset() {
    $("#login").children("a").removeClass("active");
    $("#reg").children("a").removeClass("active");
    $("#find").children("a").addClass("active");

    $("#loginpanel").removeClass("active");
    $("#regpanel").removeClass("active");
    $("#findpanel").addClass("active");

    $("#mymodal").modal("show");
}

// 登录
 function doLogin(e) {
    if (e != null && e.keyCode != 13) {
        return false
    }
    var loginname = $.trim($("#loginname").val());
    var loginpass = $.trim($("#loginpass").val());
    var logincode = $.trim($("#logincode").val());
    if (loginname.length < 5 || loginpass < 5) {
        bootbox.alert({title: "错误提示", message: "用户名或密码少于五位"});
        return false;
    } else {
        var param = "username=" + loginname;
        param += "&password=" + loginpass;
        param += "&logincode=" + logincode;
        $.post("/login", param, function (data) {
            if (data == "vcode-error") {
                bootbox.alert({title: "错误提示", message: "验证码错误且已刷新，请重新输入"});
                $("#logincode").val("");
                $("#logincode").focus();
                $("#loginvcode").attr("src",'/vcode?'+Math.random())

            } else if (data == "login-pass") {
                bootbox.alert({title: "信息提示", message: "恭喜你，登录成功"});
                setTimeout("location.reload();", 1000)
            } else if (data == "login-fail") {
                bootbox.alert({title: "错误提示", message: "没有该用户或密码错误，如有其他问题，请联系管理员"});

            }
            else if (data=="add-credit"){
                $.get("/loginEvereDayCredit",function (data){
                    var loginEvereDayCredit=data["loginEvereDayCredit"]
                qingti("登录成功，积分+"+loginEvereDayCredit)
                    bootbox.alert({title: "信息提示", message: "恭喜你登录成功"});
                setTimeout("location.reload();", 2000)

    })
            }
        })
    }

}

// 轻量级提示框
function  qingti(s) {
        toastr.info(s)
    }


// 写赞同函数
function agreeComment(s,j,n){
    $.post("/agreeComment", param="commentid="+j, function (data) {

            if(data==="1"){
                $(s).children("font").text("取消赞同("+(parseInt(n)+1).toString()+")")
                $(s).children("font").attr('color','red')
                $(s).next().css("visibility","hidden");
                // 移除响应事件
                $(s).removeAttr('onclick')
                // 修改响应事件
                $(s).click(function (){
                    cancle_agreeComment(this,j,n)
                })
                qingti("已赞同该评论")
                ;
            }
            else {
                bootbox.alert({title: "错误提示", message: "赞同失败，请联系管理员"});
            }
            }
        )
}

// 第一个参数是div的位置即:this 第二个参数为评论的commentid 第三个参数用来判断这是原始评论还是回复评论的评论
 // 第四个参数用来定位该原始评论或回复评论的评论的原始评论在这一页的位置
// 如果第三个参数为1 那定位的原始评论的div的id为"returnArticle(numLocate)" 如果为2
//  那么其评论div的id为"returnComment(numLocate)(j)"
function hideComment(s,commentid,num,numLocate,j){

    bootbox.confirm({
    title: "操作提示",
    message: "是否确定永久删除该评论",
    buttons: {
        cancel: {
            label: '<i class="fa fa-times"></i> 再考虑一下'
        },
        confirm: {
            label: '<i class="fa fa-check"></i> 确定删除'
        }
    },
    callback: function (result) {
        if (result.toString() ==="true" ){
        $.post("/hideComment", param="commentid="+commentid, function (data) {
            if (data==="1"){
                var idNum
                if(num===1){
                   idNum="#returnArticle"+numLocate.toString()
                }
                else {
                    idNum="#returnComment"+numLocate.toString()+j.toString()
                }
             $(idNum).css("display","none");
             bootbox.alert({title: "操作提示", message: "删除评论成功"});
             qingti("删除评论成功")
         }
            else {
                bootbox.alert({title: "错误提示", message: "删除评论失败，请联系管理员"});
            }
        })
    }
    }
}


     )
}


function hideComment_1(commentid){
    bootbox.confirm({
    title: "操作提示",
    message: "是否确定永久删除该评论",
    buttons: {
        cancel: {
            label: '再考虑一下'
        },
        confirm: {
            label: '确定删除'
        }
    },
    callback: function (result) {
        if (result.toString() ==="true" ){
        $.post("/hideComment", param="commentid="+commentid, function (data) {
            if (data==="1"){
            var lin="#comment__"+commentid.toString()
                $(lin).css("display","none")
             bootbox.alert({title: "操作提示", message: "删除评论成功"});
             qingti("删除评论成功")
         }
            else {
                bootbox.alert({title: "错误提示", message: "删除评论失败，请联系管理员"});
            }
        })
    }
    }
}


     )
}

// 写反对函数
function opposeComment(s,j,n){
    $.post("/disagreeComment", param="commentid="+j, function (data) {
            if(data==="1"){
                $(s).children("font").text("取消反对("+(parseInt(n)+1).toString()+")")
                $(s).children("font").attr('color','red')
                $(s).prev().css("visibility","hidden");
                // 移除响应事件
                $(s).removeAttr('onclick')
                // 修改响应事件
                $(s).click(function (){
                    cancle_opposeComment(this,j,n)
                })
                qingti("已反对该评论")
                ;

            }
            else {
                bootbox.alert({title: "错误提示", message: "反对失败，请联系管理员"});
            }
            }
        )
}

// 写取消赞同函数
function cancle_agreeComment(s,j,n){
    $.post("/cancle_agreeComment", param="commentid="+j, function (data) {
            if(data==="1"){
                $(s).children("font").text("赞同("+(parseInt(n)).toString()+")")
                $(s).children("font").attr('color','')
                $(s).next().css("visibility","visible");
                // 移除响应事件
                $(s).removeAttr('onclick')
                $(s).click(function (){
                    agreeComment(this,j,n)
                })
                ;
                qingti("已取消赞同该评论")
            }
            else {
                bootbox.alert({title: "错误提示", message: "取消赞同失败，请联系管理员"});
            }
            }
        )
}


// 写取消反对函数
function cancle_opposeComment(s,j,n){
    $.post("/cancle_disagreeComment", param="commentid="+j, function (data) {
            if(data==="1"){
                $(s).children("font").text("反对("+(parseInt(n)).toString()+")")
                $(s).children("font").attr('color','')
                $(s).prev().css("visibility","visible");
                // 移除响应事件
                $(s).removeAttr('onclick')
                $(s).click(function (){
                    opposeComment(this,j,n)
                })
                ;
                qingti("已取消反对该评论")
            }
            else {
                bootbox.alert({title: "错误提示", message: "取消反对失败，请联系管理员"});
            }
            }
        )
}


// 写跳转页面并修改文章的函数
 function  modifyArticle(articleid){
    $.post("/centerVar",param="articleid="+articleid,function (data){
        if (data==="1"){
            location.href="/prepost"
        }
    })

     }

// 自动加载的函数
// load_1函数用来自动登录
 function load_1(){ 　
    $.get("/toTransmitParam",function (param){
        var loginEvereDayCredit=param["loginEvereDayCredit"]
        $.post("/judgeAutoLogin",function (data){
        if (data==="1"){
            bootbox.alert({title: "信息提示", message: "恭喜你，登录成功"});
                qingti("每天登录成功，积分+"+loginEvereDayCredit)
                setTimeout("location.reload();", 2000)
}
    })

    })

}

// load_2函数用来判定修改文章的值（如果作者点击的是修改按钮的话）
function load_2(){ 　
    $.get("/centerVar",function (data){
        var PAN=parseInt(data)
        if (PAN===0){
            return false
}
else {
    $.get("/modifyArticle/" + PAN, function (data) {
          var headline=data["headline"]
        $("#headline").val(headline)
        $("#xiugaiwenzhang").text("修改文章")
        $("#xiugaiwenzhang").attr("onclick","doPost(" + "\'" +PAN+"\'" + "," + "\'" + 4 + "\'" +")")
        $("#biaoji1").css("display","none");
})
}
    })
}

// 修改昵称
function modifyNickname(s,yuan) {
    var newNickname = $.trim($(s).parent().prev().children("input").val());
    if (newNickname === yuan) {
        return false
    }
    else if (newNickname.length>30){
        bootbox.alert({title: "错误提示", message: "要修改的昵长度超过限制，请修改"});
        return false
    }
    bootbox.confirm({
        title: "操作提示",
        message: "是否确定修改你的昵称",
        buttons: {
            cancel: {
                label: '再考虑一下'
            },
            confirm: {
                label: '确定修改'
            }
        },
        callback: function (result) {
            if (result.toString() === "true") {
                $.post("/modifyNickname",param="newNickname="+newNickname,function (data) {
                    if(data==="1"){
                        qingti("修改昵称成功")
                        $(s).parent().prev().children("input").attr("value", newNickname)
                        $(s).parent().prev().children("input").focus()
                    }
                    else {
                         bootbox.alert({title: "错误提示", message: "修改昵称失败，请联系管理员"});
                    }

                })
            }
        }

    })
}

// 申请成为编辑
 function applyEditor(s){
    bootbox.confirm({
        title: "操作提示",
        message: "是否申请成为编辑,经过管理员同意后，编辑可直接不经过管理员审核而发布文章",
        buttons: {
            cancel: {
                label: '再考虑一下'
            },
            confirm: {
                label: '确定申请'
            }
        },
        callback: function (result) {
            if (result.toString() === "true") {
                $.post("/applyEditor",function (data){
                    if (data==="1"){
                        bootbox.alert({title: "操作提示", message: "申请成功，请等待管理员的审核"});
                        $(s).text("已申请")
                    }
                })
            }
        }

    })
 }

// 修改qq号
 function modifyQQ(s,yuan) {
    var newQQ = $.trim($(s).parent().prev().children("input").val());
    var reg = new RegExp("^[0-9]*$");
    if (newQQ === yuan) {
        return false
    }
    else if (newQQ.length>11||!reg.test(newQQ)){
        bootbox.alert({title: "错误提示", message: "QQ号格式错误，请重试"});
        return false
    }
    bootbox.confirm({
        title: "操作提示",
        message: "是否确定修改你的QQ",
        buttons: {
            cancel: {
                label: '再考虑一下'
            },
            confirm: {
                label: '确定修改'
            }
        },
        callback: function (result) {
            if (result.toString() === "true") {
                $.post("/modifyQQ",param="newQQ="+newQQ,function (data) {
                    if(data==="1"){
                        qingti("修改QQ成功")
                        $(s).parent().prev().children("input").attr("value", newQQ)
                        $(s).parent().prev().children("input").focus()
                    }
                    else {
                         bootbox.alert({title: "错误提示", message: "修改QQ失败，请联系管理员"});
                    }

                })
            }
        }

    })
}

// 删除文章
 function hideArticle(articleid){
    bootbox.confirm({
        title: "操作提示",
        message: "是否确定永久删除该文章",
        buttons: {
            cancel: {
                label: '再考虑一下'
            },
            confirm: {
                label: '确定删除'
            }
        },
        callback: function (result) {
            if (result.toString() === "true") {
                $.post("/hideArticle",param="articleid="+articleid,function (data) {
                    if(data==="1"){
                        qingti("删除文章成功")
                        var lin="#article__"+articleid
                        $(lin).css("display","none")
                        var num= $("#allMyArticleNum").text()
                        var newNum=parseInt(num)-1
                        $("#allMyArticleNum").text(newNum)

                    }
                    else {
                         bootbox.alert({title: "错误提示", message: "删除文章失败，请联系管理员"});
                    }

                })
            }
        }

    })
 }

// 更改userManage模块的函数
 function changeUserManageModel(m){
    $("#myInfo_1").removeClass("active");
    $("#myArticle_1").removeClass("active");
    $("#myComment_1").removeClass("active");
    $("#myContact_1").removeClass("active");
    $("#myCredit_1").removeClass("active");
    $("#myLog_1").removeClass("active");
    $("#myFavo_1").removeClass("active");
    $("#getCredit_1").removeClass("active");

    $("#myInfo").css("display","none")
    $("#myArticle").css("display","none")
    $("#myComment").css("display","none")
    $("#myContact").css("display","none")
    $("#myCredit").css("display","none")
    $("#myLog").css("display","none")
    $("#myFavo").css("display","none")
    $("#getCredit").css("display","none")

     var tiao="0"
     if (m==="myInfo_1"){
        tiao="0";
     }
     else if(m==="myArticle_1")
     {tiao="1";

     }
     else if(m==="myComment_1")
     {tiao="2";

     }
     else if(m==="myCredit_1")
     {tiao="3";

     }
     else if(m==="myContact_1")
     {tiao="4";

     }
     else if(m==="myLog_1")
     {tiao="5";

     }
     else if(m==="myFavo_1")
     {tiao="6";

     }
     else if(m==="getCredit_1")
     {tiao="7";

     }
     $.post("/controlBiaoNum",param="controlBiaoNum="+tiao,function (data){
         return false
     })


    var mainContent=("#"+m).slice(0,-2)

    $("#"+m).addClass("active");
    $(mainContent).css("display","block")
 }

// 更改管理页面中文章分页
 function changeManagePage(id,howManyPage,everyPageInHou,myArticleNum){
    howManyPage=parseInt(howManyPage)
    everyPageInHou=parseInt(everyPageInHou)
    myArticleNum=parseInt(myArticleNum)
    id=parseInt(id)
    var arr = [1];
    for(var i = 2; i <= howManyPage; i++){
      arr.push(i);
    }
    for (const v of arr) {
        var lin="#biao_"+v.toString()
        $(lin).removeClass("active")

    }
    lin="#biao_"+id.toString()
     $(lin).addClass("active")

     //上面是变化下面的页数

     var arr1=[]
     for(var j = 1; j <= myArticleNum; j++){
      arr1.push(j);
    }

     for (const w of arr1) {
        var lin_1=".index_"+w.toString()
        $(lin_1).css("display","none")
    }

     if (myArticleNum<everyPageInHou){
         var arr5=[]
         for(var mn1 = 1; mn1 <= myArticleNum; mn1++){
        arr5.push(mn1);
    }

         for (const op1 of arr5) {
        var lin_6=".index_"+op1.toString()
        $(lin_6).css("display","")
    }
     }
     else {
         if(id===1){
         var arr4=[]
         for(var mn = 1; mn <= everyPageInHou; mn++){
        arr4.push(mn);
    }

         for (const op of arr4) {
        var lin_5=".index_"+op.toString()
        $(lin_5).css("display","")
    }
     }
     else {
         if (id<howManyPage){
         var arr2=[]
         for(var k = (id-1)*everyPageInHou+1; k <= id*everyPageInHou; k++){
        arr2.push(k);
    }

         for (const p of arr2) {
        var lin_3=".index_"+p.toString()
        $(lin_3).css("display","")
    }
     }
     else {
         var arr3=[]
         for(var l = (id-1)*everyPageInHou+1; l <= myArticleNum; l++){
        arr3.push(l);
    }

         for (const y of arr3) {
        var lin_4=".index_"+y.toString()
        $(lin_4).css("display","")
    }

     }

     }
     }






 }

 // 跳转到指定文章
 function tiaoArticle(articleid,n){
    location.href="/article/"+articleid.toString();
    $.post("/controlBiaoNum",param="controlBiaoNum="+n.toString(),function (data){
        return false
    })
 }

 // 取消收藏
 function cancel_favorite(articleid,n=-1) {
        $.ajax({
            url: "/favorite/" + articleid,
            type: "delete",
            success: function (data) {
                if (data == "not-login") {
                    bootbox.alert({title: "错误提示", message: "请先登录本界面"})
                } else if (data == "cancel-pass") {
                    bootbox.alert({title: "信息提示", message: "取消收藏成功"})
                    //    菜单名称改为感谢收藏
                    $(".favorite-btn").html('<span class=\"oi oi-heart \" aria-hidden=\"true\" ></span> 欢迎再来')
                    //    取消收藏按钮的单击事件
                    $(".favorite-btn").attr("onclick", "").unbind("click");
                    if(n===-1){
                        return false
                    }
                    else {
                        var lin="#favorite__"+n.toString();
                        $(lin).hide()
                    }

                } else {
                    bootbox.alert({title: "错误提示", message: "取消收藏失败，请联系管理员"})
                }
            }
        })
    }



// 添加文章收藏
 function add_favorite(articleid) {
        $.post("/favorite", "articleid=" + articleid, function (data) {
            if (data == "not-login") {
                bootbox.alert({title: "错误提示", message: "请先登录本界面"})
            } else if (data == "favorite-pass") {
                bootbox.alert({title: "信息提示", message: "本文收藏成功，可在我的收藏中查看,再次刷新页面可选择取消收藏"})
                //    菜单名称改为感谢收藏
                $(".favorite-btn").html('<span class=\"oi oi-heart \" aria-hidden=\"true\" style=\"color: red\"></span> 感谢收藏')
                //    取消收藏按钮的单击事件
                $(".favorite-btn").attr("onclick", "").unbind("click");
            } else {
                bootbox.alert({title: "错误提示", message: "收藏失败，请联系管理员"})
            }
        })
    }

 // 添加评论
 function addCommnet(articleid) {
        var content = $.trim($("#comment").val());
        if (content.length < 5 || content.length > 1000) {
            bootbox.alert({title: "错误提示", message: "评论内容在5~1000字之间"});
            return false
        }
        var param = "articleid=" + articleid + "&content=" + content;
        $.post("/comment", param, function (data) {
            if (data == "not-login") {
                bootbox.alert({title: "错误提示", message: "请先登录再评论"});
            } else if (data == "add-limit") {
                bootbox.alert({title: "错误提示", message: "您当天最多只能评论五次"});

            } else if (data == "add-pass") {
                $.get("/toTransmitParam",function (data){
                    var replyAndAddCommentCredit=data["replyAndAddCommentCredit"]
                qingti("回复评论成功，积分+"+replyAndAddCommentCredit)
                setTimeout("location.reload();", 2000)

    })


            } else {
                bootbox.alert({title: "错误提示", message: "发表评论出错，请联系管理员"});

            }
        })
    }

 // 填充评论（前端填充）
 function fillComment(articleid, pageid) {
        $("#commentDiv").empty();  // 清空现有评论
        var content = "";
        $.get("/comment/" + articleid + "-" + pageid, function (data) {
            var comment = data;
            for (var i in comment) {
                content += `<div class="col-12 list row" id="returnArticle${i}" style="">`;
                content += '<div class="col-2 icon">';
                content += '<img src="/static/img/avatar/' + comment[i]['avatar'] + '"class="img-fluid" style="width: 80px;height: 80px;border-radius: 50%"/>';
                content += '</div>'
                content += '<div class="col-10 comment">'
                content += '<div class="col-12 row" style="padding: 0px">'
                content += '<div class="col-sm-6 col-12 commenter">';
                content += comment[i]["nickname"];
                content += '&nbsp;&nbsp;&nbsp;' + comment[i]["createtime"];
                content += '</div>';
                content += '<div class="col-sm-6 col-12 reply">';

                if ("{{article.userid}}" === "{{session.get('userid')}}" ||
                    "{{session.get('role')}}" == "admin" || comment[i]['userid'] + "" == "{{session.get('userid')}}") {
                    content += '<label onclick="gotoReply(' + comment[i]['commentid'] + ')"';
                    content += '<span class="oi oi-arrow-circle-right"aria-hidden="true"></span> ';
                    content += '回复</label>&nbsp;&nbsp;&nbsp;'
                    content += `<label onclick="hideComment(this,${comment[i]['commentid']},1,${i},-1)"`;

                    content += '<span class="oi oi-delete"aria-hidden="true"></span>删除评论</label> ';
                } else {
                    if (comment[i]["agreeOrdisAgreeType"] === 0) {
                        content += `<label onclick="gotoReply(${comment[i]['commentid']})">
                                            <span class="oi oi-arrow-circle-right" aria-hidden="true"></span>回复
                                        </label>&nbsp;&nbsp;

                                        <label onclick="agreeComment(this,${comment[i]["commentid"]},${comment[i]["agreecount"]})" style="visibility: visible;" id="agreeComment1">
                                            <span class="oi oi-chevron-bottom"
                                                  aria-hidden="true"></span><font>赞成(<span>${comment[i]["agreecount"]}</span>)</font>
                                        </label>&nbsp;&nbsp;

                                        <label onclick="opposeComment(this,${comment[i]["commentid"]},${comment[i]["opposecount"]})" style="visibility: visible;" id="opposeComment1">
                                <font color=""><span class="oi oi-x"
                                      aria-hidden="true"></span>反对(<span>${comment[i]["opposecount"]}</span>)</font>
                                        </label>`
                    } else if (comment[i]["agreeOrdisAgreeType"] === 1) {
                        content += `<label onclick="gotoReply(${comment[i]['commentid']})">
                                            <span class="oi oi-arrow-circle-right" aria-hidden="true"></span>回复
                                        </label>&nbsp;&nbsp;

                                        <label onclick="cancle_agreeComment(this,${comment[i]["commentid"]},${comment[i]["agreecount"]})" style="visibility: visible;" id="agreeComment1">
                                            <span class="oi oi-chevron-bottom"
                                                  aria-hidden="true"></span><font color="red">取消赞成(<span>${comment[i]["agreecount"]}</span>)</font>
                                        </label>&nbsp;&nbsp;

                                        <label onclick="opposeComment(this,${comment[i]["commentid"]},${comment[i]["opposecount"]})" style="visibility: hidden;" id="opposeComment1">
                                <font color=""><span class="oi oi-x"
                                      aria-hidden="true"></span>反对(<span>${comment[i]["opposecount"]}</span>)</font>
                                        </label>`
                    } else if (comment[i]["agreeOrdisAgreeType"] === -1) {
                        content += `<label onclick="gotoReply(${comment[i]['commentid']})">
                                            <span class="oi oi-arrow-circle-right" aria-hidden="true"></span>回复
                                        </label>&nbsp;&nbsp;

                                        <label onclick="agreeComment(this,${comment[i]["commentid"]},${comment[i]["agreecount"]})" style="visibility: hidden;" id="agreeComment1">
                                            <span class="oi oi-chevron-bottom"
                                                  aria-hidden="true"></span><font>赞成(<span>${comment[i]["agreecount"]}</span>)</font>
                                        </label>&nbsp;&nbsp;

                                        <label onclick="cancle_opposeComment(this,${comment[i]["commentid"]},${comment[i]["opposecount"]})" style="visibility: hidden id="opposeComment1">
                                <font color="red"><span class="oi oi-x"
                                      aria-hidden="true"></span>取消反对(<span>${comment[i]["opposecount"]}</span>)</font>
                                        </label>`
                    }
                }
                content += '</div>';
                content += '</div>';
                content += '<div class="col-12 content">';
                content += comment[i]["content"];
                content += '</div>';
                content += '</div>';
                content += '</div>';

                //    在当前评论下面填充回复评论
                if (comment[i]["reply_list"].length > 0) {
                    var reply = comment[i]["reply_list"];
                    for (var j in reply) {
                        content += `<div class="col-12 list row" id="returnComment${i}${j}" style="">`;
                        content += '<div class="col-2 icon">';
                        content += '<img src="/static/img/avatar/' + reply[j]["avatar"] + '"class="img-fluid" style="width:55px;height: 55px;border-radius: 50%"/>';
                        content += '</div>';
                        content += '<div class="col-10 comment" style="border: solid 1px #ccc;">';
                        content += '<div class="col-12 row" style="color: #337AB7;">';
                        content += '<div class="col-sm-7 col-12 commenter" style="color:#337AB7;">';

                        //    填充用户昵称
                        content += reply[j]["nickname"]
                        content += "回复";
                        content += comment[i]["nickname"];
                        content += '&nbsp;&nbsp;&nbsp;';
                        content += reply[j]["createtime"];
                        content += '</div>';
                        content += '<div class="col-sm-5 col-12 reply">';

                        //    回复的评论不能继续评论，但可以删除评论和点赞(作者或管理员的话)
                        if ("{{article.userid}}" == "{{session.get('userid')}}" ||
                            "{{session.get('role')}}" == "admin" || reply[j]["userid"] + "" == "{{session.get('userid')}}") {
                            content += `<label onclick="hideComment(this,${reply[j]["commentid"]},2,${i},${j})">`;
                            content += '<span class="oi oi-delete" aria-hideen="true"></span>删除评论';
                            content += '</label>&nbsp;&nbsp;';
                        }
                        if (comment[i]["agreeOrdisAgreeType"] === 0) {
                            content += `<label onclick="agreeComment(this,${comment[i]["commentid"]},${comment[i]["agreecount"]})" style="visibility: visible;" id="agreeComment1">
                                            <span class="oi oi-chevron-bottom"
                                                  aria-hidden="true"></span><font>赞成(<span>${comment[i]["agreecount"]}</span>)</font>
                                        </label>&nbsp;&nbsp;

                                        <label onclick="opposeComment(this,${comment[i]["commentid"]},${comment[i]["opposecount"]})" style="visibility: visible;" id="opposeComment1">
                                <font color=""><span class="oi oi-x"
                                      aria-hidden="true"></span>反对(<span>${comment[i]["opposecount"]}</span>)</font>
                                        </label>`
                        } else if (comment[i]["agreeOrdisAgreeType"] === 1) {
                            content += `<label onclick="cancle_agreeComment(this,${comment[i]["commentid"]},${comment[i]["agreecount"]})" style="visibility: visible;" id="agreeComment1">
                                            <span class="oi oi-chevron-bottom"
                                                  aria-hidden="true"></span><font color="red">取消赞成(<span>${comment[i]["agreecount"]}</span>)</font>
                                        </label>&nbsp;&nbsp;

                                        <label onclick="opposeComment(this,${comment[i]["commentid"]},${comment[i]["opposecount"]})" style="visibility: hidden;"  id="opposeComment1">
                                <font color=""><span class="oi oi-x"
                                      aria-hidden="true"></span>反对(<span>${comment[i]["opposecount"]}</span>)</font>
                                        </label>`
                        } else if (comment[i]["agreeOrdisAgreeType"] === -1) {
                            content += `<label onclick="agreeComment(this,${comment[i]["commentid"]},${comment[i]["agreecount"]})" style="visibility: hidden;" id="agreeComment1">
                                            <span class="oi oi-chevron-bottom"
                                                  aria-hidden="true"></span><font>赞成(<span>${comment[i]["agreecount"]}</span>)</font>
                                        </label>&nbsp;&nbsp;
                                        <label onclick="cancle_opposeComment(this,${comment[i]["commentid"]},${comment[i]["opposecount"]})" style="visibility:visible;" id="opposeComment1">
                                <font color="red"><span class="oi oi-x"
                                      aria-hidden="true"></span>取消反对(<span>${comment[i]["opposecount"]}</span>)</font>
                                        </label>`
                        }

                        content += '</div>';
                        content += '</div>';
                        content += '<div class="col-12">';
                        content += '回复内容' + reply[j]["content"];
                        content += '</div>';
                        content += '</div>';
                        content += '</div>';


                    }
                }
            }
            $("#commentDiv").html(content);  //填充到评论区

        });
    }

 //  回复原始评论
 function replyComment(articleid) {
        var content = $.trim($("#comment").val());
        if (content.length < 5 || content.length > 1000) {
            bootbox.alert({title: "错误提示", message: "评论内容再5~1000字之间"});
            return false
        }
        var param = "articleid=" + articleid;
        param += "&content=" + content;
        param += "&commentid=" + COMMENTID;
        $.post("/reply", param, function (data) {
            if (data == "not-login") {
                bootbox.alert({title: "错误提示", message: "请先登录"});
            } else if (data == "reply-limit") {
                bootbox.alert({title: "错误提示", message: "当天已用完五次评论的限额"});
            } else if (data == "reply-pass") {
                $.get("/replyAndAddCommentCredit",function (data){
                    var replyAndAddCommentCredit=data["replyAndAddCommentCredit"]
                qingti("回复评论成功，积分+"+replyAndAddCommentCredit)
                setTimeout("location.reload();", 2000)

    })
                gotoPage(articleid,PAGE)

            } else if (data == "reply-fail") {
                bootbox.alert({title: "错误提示", message: "回复评论错误，请联系管理员"});
            }
        })

    }

 // 添加文章的评论
 function gotoReply(commentid) {
        $("#replyBtn").show();
        $("#submitBtn").hide();
        if ("{{session.get('islogin')}}" === "true") {
            $("#nickname_1").val("请在此回复编号为" + commentid + "的评论");
        } else {
            $("#nickname_2").val("请在此回复编号为" + commentid + "的评论");
        }

        $("#comment").focus();
        COMMENTID = commentid;

    }

 // 评论跳转到哪一页
 function gotoPage(articleid, type) {
        //    如果当前是第一页，那么上一页还是第一页
        if (type === "prev") {
            if (PAGE > 1) {
                PAGE -= 1;
            }
        } else if (type === "next") {
            if (PAGE < TOTAL) {
                PAGE += 1;
            }
        } else {
            PAGE = parseInt(type);
        }
        fillComment(articleid, PAGE)
    }

// 定义搜索函数
function dosearch(e) {
        if (e != null && e.keyCode != 13) {
            return false
        }
        var keyword = $.trim($("#keyword").val());
        if (keyword.length === 0 || keyword.length > 10 || keyword.indexOf("%") >= 0) {
            bootbox.alert({"title": "错误提示", "message": "你输入的关键字不合法"});
            $("#keyword").focus();
            return false
        }
        location.href = "/search/1-" + keyword;
    }

// 截取字符串
function truncate(headline, length) {
        var count = 1;
        var output = "";
        for (var i in headline) {
            output += headline.charAt(i);
            var code = headline.charCodeAt(i);
            if (code <= 128) {
                count += 0.5;
            } else {
                count += 1;
            }
            if (count > length) {
                break;
            }
        }
        return output + "..."

    }

//   定义删除多个文章的函数
function delMany(){
				var names=document.getElementsByName("checkbox[]");
                var arr=[]
                bootbox.confirm({
        title: "操作提示",
        message: "是否确定删除文章",
        buttons: {
            cancel: {
                label: '再考虑一下'
            },
            confirm: {
                label: '确定修改'
            }
        },
        callback: function (result) {
            if (result.toString() === "true") {
                for(var x=0;x<names.length;x++){
					if(names[x].checked){//选中的全部加起来
						arr.push(parseInt(names[x].value));//将选中的值添加到一个列表

					}
				}
                for (const w of arr) {

        $.post("/hideArticle",param="articleid="+w.toString(),function (data) {
                    if(data==="1"){
                        return false
                    }
                    else {
                         bootbox.alert({title: "错误提示", message: "删除文章失败，请联系管理员"});
                    }

                })


    }
                $.post("/controlBiaoNum",param="controlBiaoNum="+"1",function (data){
                    if (data==="1"){
                        qingti("删除文章成功")
                bootbox.alert({title: "操作提示", message: "删除文章成功"});
                setTimeout(function (){location.reload()}, 1000)
                    }
                    else {
                        bootbox.alert({title: "操作提示", message: "删除文章失败，请联系管理员"});
                    }

                })





            }
        }

    })



			}




