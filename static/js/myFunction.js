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
             bootbox.alert({title: "操作提示", message: "删除评论成功，可在用户中心查看记录"});
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
    else if (newNickname.length<30){
        bootbox.alert({title: "错误提示", message: "要修改的昵称超过限制，请修改"});
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

    $("#myInfo").css("display","none")
    $("#myArticle").css("display","none")
    $("#myComment").css("display","none")
    $("#myContact").css("display","none")
    $("#myCredit").css("display","none")
    $("#myLog").css("display","none")
    $("#myFavo").css("display","none")

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