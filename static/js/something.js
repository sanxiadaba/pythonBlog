function doSendMail(obj) {
    var email = $.trim($("#regname").val());
    if (!email.match(/.+@.+\..+/)) {
        bootbox.alert({title: "错误提示", message: "邮箱格式不正确"});
        $("#regname").focus;
        return false;
    }
    $.post("/ecode", "email=" + email, function (data) {
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
            bootbox.alert({title: "错误提示", message: "邮箱验证码未发送成功"});
            return false;
        }
    })
}

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
                bootbox.alert({title: "错误提示", message: "验证码无效"})
                $("#regmcode_1").val(""); //清除验证码的值
                $("#regmcode_1").focus(); // 让验证码框获取到焦点供用户输入
            } else if (data == "up-invalid") {
                bootbox.alert({title: "错误提示", message: "注册邮箱不正确或密码少于5位"})
            } else if (data == "reg-pass") {
                bootbox.alert({title: "信息提示", message: "恭喜你注册成功"})
                qingti("注册成功，已增加50积分")
                // 注册成功后 延迟一秒钟刷新当前页面
                setTimeout("location.reload();", 1000)
            } else if (data == "reg-fail") {
                bootbox.alert({title: "错误提示", message: "注册失败，请联系管理员"})
            }
        })
    }

}

function showLogin() {
    $("#login").addClass("active");
    $("#reg").removeClass("active");
    $("#find").removeClass("active");
    $("#loginpanel").addClass("active");
    $("#regpanel").removeClass("active");
    $("#findpanel").removeClass("active");
    $("#mymodal").modal("show");
}

function showReg() {
    $("#login").removeClass("active");
    $("#reg").addClass("active");
    $("#find").removeClass("active");
    $("#loginpanel").removeClass("active");
    $("#regpanel").addClass("active");
    $("#findpanel").removeClass("active");
    $("#mymodal").modal("show");
}

function showReset() {
    $("#login").removeClass("active");
    $("#reg").removeClass("active");
    $("#find").addClass("active");
    $("#loginpanel").removeClass("active");
    $("#regpanel").removeClass("active");
    $("#findpanel").addClass("active");
    $("#mymodal").modal("show");
}


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
                bootbox.alert({title: "错误提示", message: "验证码无效，请点击验证码刷新后尝试"});
                $("#loginvcode").val("");
                $("#loginvcode").focus();

            } else if (data == "login-pass") {
                bootbox.alert({title: "信息提示", message: "恭喜你，登陆成功"});
                setTimeout("location.reload();", 1000)
            } else if (data == "login-fail") {
                bootbox.alert({title: "错误提示", message: "没有该用户或密码错误，如有其他问题，请练习管理员"});

            }
            else if (data=="add-credit"){
                bootbox.alert({title: "信息提示", message: "恭喜你，登陆成功"});
                qingti("每天登录成功，积分+1")
                setTimeout("location.reload();", 1000)

            }
        })
    }

}

function  qingti(s) {
        toastr.info(s)
    }



