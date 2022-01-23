// Send email verification code
// The n in the parameter is used to determine whether to send a registration verification code or a password recovery verification code
function doSendMail(obj,n) {
    var email=""
    if(n===1){
        email = $.trim($("#regname").val());
    }
    else {
        email = $.trim($("#finame").val());
    }

    if (!email.match(/.+@.+\..+/)) {
        bootbox.alert({title: "Error Alert", message: "Incorrect email format"});
        $("#regname").focus;
        return false;
    }
    $.post("/ecode", "email=" + email+"&n="+n, function (data) {
        if (data == "eamil-invalid") {
            bootbox.alert({title: "Error Alert", message: "Incorrect email address format"});
            $("#regname").focus;
            return false;
        }

        if (data == "send-pass") {
            bootbox.alert({title: "Information Tips", message: "E-mail has been successfully sent, please check"});
            $("#regname").attr("disabled", true);// After the verification code is sent, it is forbidden to modify the registered email address.
            $(obj).attr("disabled", true); //Send Email button becomes unavailable
            return false;
        } else {
            bootbox.alert({title: "Error Alert", message: "E-mail verification code was not sent successfully, please contact the administrator"});
            return false;
        }
    })
}

// Registration
function doRegister(e) {
    if (e != null && e.keyCode != 13) {
        return false
    }

    var regname = $.trim($("#regname").val());
    var regpass = $.trim($("#regpass").val());
    var regcode = $.trim($("#regcode").val());

    if (!regname.match(/.+@.+\..+/) || regpass.length < 5) {
        bootbox.alert({title: "Error Alert", message: "Incorrect registration email or password less than five digits"});
        return false;
    } else {
        // Build post request body
        var param = "username=" + regname;
        param += "&password=" + regpass;
        param += "&ecode=" + regcode;
        // Sending post requests using the jquery framework
        $.post("/user", param, function (data) {
            if (data == "ecode-error") {
                bootbox.alert({title: "Error Alert", message: "Error in verification code"})
                $("#regcode").val(""); //Clear the value of the CAPTCHA
                $("#regcode").focus(); // Let the captcha box get the focus for the user to enter
            } else if (data == "up-invalid") {
                bootbox.alert({title: "Error Alert", message: "Incorrect registration email or password less than 5 digits"})
            } else if (data == "reg-pass") {
                bootbox.alert({title: "Information Tips", message: "Congratulations on your successful registration!"})
                // After successful registration, there is a two-second delay in refreshing the current page
                $.get("/replyAndAddCommentCredit",function (data){
                    var regGiveCredit=data["regGiveCredit"]
                qingti("Registration was successful and has been added"+regGiveCredit+"Points")

    })

                setTimeout("location.reload();", 2000)
            } else if (data == "reg-fail") {
                bootbox.alert({title: "Error Alert", message: "Registration failed, please contact the administrator"})
            }
            else if (data=="user-repeated"){
        bootbox.alert({title: "Error Alert", message: "This account is registered"})
            }
            else if (data==="ecode-timeout"){
                bootbox.alert({title: "Error Alert", message: "The verification code has expired"})
            }
        })
    }

}

// Retrieve password
 function findPassword(e){
    if (e != null && e.keyCode != 13) {
        return false
    }

    var finame = $.trim($("#finame").val());
    var fipass = $.trim($("#fipass").val());
    var ficode = $.trim($("#ficode").val());

    if (!finame.match(/.+@.+\..+/) || fipass.length < 5) {
        bootbox.alert({title: "Error Alert", message: "Incorrect email address or password less than five digits"});
        return false;
    } else {
        // Build post request body
        var param = "username=" + finame;
        param += "&password=" + fipass;
        param += "&ecode=" + ficode;
        // Sending post requests using the jquery framework
        $.post("/resetUserPassword", param, function (data) {
            if(data=="no-user"){
                bootbox.alert({title: "Error Alert", message: "The user was not found and the password could not be reset"})
            }
            else if (data == "ecode-error") {
                bootbox.alert({title: "Error Alert", message: "Error in verification code"})
                $("#ficode").val(""); //Clear the value of the CAPTCHA
                $("#ficode").focus(); // Let the captcha box get the focus for the user to enter
            } else if (data == "up-invalid") {
                bootbox.alert({title: "Error Alert", message: "Incorrect email address or password less than 5 digits"})
            } else if (data == "fi-pass") {
                qingti("Retrieve password successfully")
                setTimeout(function (){}, 1500)
                bootbox.alert({title: "Information Tips", message: "Reset password successfully, please log in again",callbacks:function (){location.reload()}})
                showLogin()
            } else if (data == "fi-fail") {
                bootbox.alert({title: "Error Alert", message: "Failed to retrieve password, please contact the administrator"})
            }
            else if (data==="ecode-timeout"){
                bootbox.alert({title: "Error Alert", message: "The verification code has expired"})
            }
        })
    }

}

// Show Login Module
function showLogin() {

    $("#login").children("a").addClass("active");
    $("#reg").children("a").removeClass("active");
    $("#find").children("a").removeClass("active");


    $("#loginpanel").addClass("active");
    $("#regpanel").removeClass("active");
    $("#findpanel").removeClass("active");

    $("#mymodal").modal("show");
}



// Show Registration
function showReg() {
    $("#login").children("a").removeClass("active");
    $("#reg").children("a").addClass("active");
    $("#find").children("a").removeClass("active");

    $("#loginpanel").removeClass("active");
    $("#regpanel").addClass("active");
    $("#findpanel").removeClass("active");

    $("#mymodal").modal("show");
}

// Show Reset Password
function showReset() {
    $("#login").children("a").removeClass("active");
    $("#reg").children("a").removeClass("active");
    $("#find").children("a").addClass("active");

    $("#loginpanel").removeClass("active");
    $("#regpanel").removeClass("active");
    $("#findpanel").addClass("active");

    $("#mymodal").modal("show");
}

// Login
 function doLogin(e) {
    if (e != null && e.keyCode != 13) {
        return false
    }
    var loginname = $.trim($("#loginname").val());
    var loginpass = $.trim($("#loginpass").val());
    var logincode = $.trim($("#logincode").val());
    if (loginname.length < 5 || loginpass < 5) {
        bootbox.alert({title: "Error Alert", message: "Username or password less than five bits"});
        return false;
    } else {
        var param = "username=" + loginname;
        param += "&password=" + loginpass;
        param += "&logincode=" + logincode;
        $.post("/login", param, function (data) {
            if (data == "vcode-error") {
                bootbox.alert({title: "Error Alert", message: "The verification code is wrong and has been refreshed, please re-enter"});
                $("#logincode").val("");
                $("#logincode").focus();
                $("#loginvcode").attr("src",'/vcode?'+Math.random())

            } else if (data == "login-pass") {
                bootbox.alert({title: "Information Tips", message: "Congratulations, your login was successful!"});
                setTimeout("location.reload();", 1000)
            } else if (data == "login-fail") {
                $("#loginvcode").attr("src",'/vcode?'+Math.random())
                bootbox.alert({title: "Error Alert", message: "No such user or wrong password, if you have other questions, please contact the administrator (verification code has been refreshed)"});

            }
            else if (data=="add-credit"){
                $.get("/loginEvereDayCredit",function (data){
                    var loginEvereDayCredit=data["loginEvereDayCredit"]
                qingti("Login successfully, points+"+loginEvereDayCredit)
                    bootbox.alert({title: "Information Tips", message: "Congratulations on your successful login!"});
                setTimeout("location.reload();", 2000)

    })
            }
        })
    }

}

// Lightweight alert box
function  qingti(s) {
        toastr.info(s)
    }


// Write approval function
function agreeComment(s,j,n){
    $.post("/agreeComment", param="commentid="+j, function (data) {

            if(data==="1"){
                $(s).children("font").text("Cancel endorsement("+(parseInt(n)+1).toString()+")")
                $(s).children("font").attr('color','red')
                $(s).next().css("visibility","hidden");
                // Remove response events
                $(s).removeAttr('onclick')
                // Modify response events
                $(s).click(function (){
                    cancle_agreeComment(this,j,n)
                })
                qingti("Have agreed with the comment")
                ;
            }
            else {
                bootbox.alert({title: "Error Alert", message: "Agree to fail, please contact the administrator"});
            }
            }
        )
}

// The first parameter is the location of the div i.e. :this The second parameter is the commentid of the comment The third parameter is used to determine whether this is the original comment or a reply to the comment
 // The fourth parameter is used to locate the original comment on this page for the original comment or the comment in reply to the comment
// if the third parameter is 1, then the id of the original comment div is "returnArticle(numLocate)" if it is 2
// then the id of its comment div is "returnComment(numLocate)(j)"
function hideComment(s,commentid,num,numLocate,j){

    bootbox.confirm({
    title: "Operation Tips",
    message: "Is it OK to permanently delete the comment",
    buttons: {
        cancel: {
            label: '<i class="fa fa-times"></i> Reconsider'
        },
        confirm: {
            label: '<i class="fa fa-check"></i> OK to delete'
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
             bootbox.alert({title: "Operation Tips", message: "Delete comment successfully"});
             qingti("删除评论成功")
         }
            else {
                bootbox.alert({title: "Error Alert", message: "Delete comment failed, please contact the administrator"});
            }
        })
    }
    }
}


     )
}


function hideComment_1(commentid){
    bootbox.confirm({
    title: "Operation Tips",
    message: "Is it OK to permanently delete the comment",
    buttons: {
        cancel: {
            label: 'Reconsider'
        },
        confirm: {
            label: 'OK to delete'
        }
    },
    callback: function (result) {
        if (result.toString() ==="true" ){
        $.post("/hideComment", param="commentid="+commentid, function (data) {
            if (data==="1"){
            var lin="#comment__"+commentid.toString()
                $(lin).css("display","none")
             bootbox.alert({title: "Operation Tips", message: "Delete comment successfully"});
             qingti("Delete comment successfully")
         }
            else {
                bootbox.alert({title: "Error Alert", message: "Delete comment failed, please contact the administrator"});
            }
        })
    }
    }
}


     )
}

// Writing the opposition function
function opposeComment(s,j,n){
    $.post("/disagreeComment", param="commentid="+j, function (data) {
            if(data==="1"){
                $(s).children("font").text("Cancel Objections("+(parseInt(n)+1).toString()+")")
                $(s).children("font").attr('color','red')
                $(s).prev().css("visibility","hidden");
                // Remove response events
                $(s).removeAttr('onclick')
                // Modify response events
                $(s).click(function (){
                    cancle_opposeComment(this,j,n)
                })
                qingti("Have objected to the comment")
                ;

            }
            else {
                bootbox.alert({title: "Error Alert", message: "Objection failed, please contact the administrator"});
            }
            }
        )
}

// Write the cancel endorsement function
function cancle_agreeComment(s,j,n){
    $.post("/cancle_agreeComment", param="commentid="+j, function (data) {
            if(data==="1"){
                $(s).children("font").text("Agree with("+(parseInt(n)).toString()+")")
                $(s).children("font").attr('color','')
                $(s).next().css("visibility","visible");
                // Remove response events
                $(s).removeAttr('onclick')
                $(s).click(function (){
                    agreeComment(this,j,n)
                })
                ;
                qingti("Disapproved the comment")
            }
            else {
                bootbox.alert({title: "Error Alert", message: "Cancel approval failed, please contact the administrator"});
            }
            }
        )
}


// Write cancel objection function
function cancle_opposeComment(s,j,n){
    $.post("/cancle_disagreeComment", param="commentid="+j, function (data) {
            if(data==="1"){
                $(s).children("font").text("Against("+(parseInt(n)).toString()+")")
                $(s).children("font").attr('color','')
                $(s).prev().css("visibility","visible");
                // Remove response events
                $(s).removeAttr('onclick')
                $(s).click(function (){
                    opposeComment(this,j,n)
                })
                ;
                qingti("Unopposed this comment")
            }
            else {
                bootbox.alert({title: "Error Alert", message: "Cancel objection failed, please contact the administrator"});
            }
            }
        )
}


// Write functions to jump pages and modify articles
 function  modifyArticle(articleid){
    $.post("/centerVar",param="articleid="+articleid,function (data){
        if (data==="1"){
            location.href="/prepost"
        }
    })

     }

// Functions for automatic loading
// The load_1 function is used to automatically log in
 function load_1(){ 　
    $.get("/toTransmitParam",function (param){
        var loginEvereDayCredit=param["loginEvereDayCredit"]
        $.post("/judgeAutoLogin",function (data){
        if (data==="1"){
            bootbox.alert({title: "Information Tips", message: "Congratulations, your login was successful!"});
                qingti("Daily login success and points+"+loginEvereDayCredit)
                setTimeout("location.reload();", 2000)
}
    })

    })

}

// The load_2 function is used to determine the value of the modified article (if the author is clicking on the modify button)
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
        $("#xiugaiwenzhang").text("Modify article")
        $("#xiugaiwenzhang").attr("onclick","doPost(" + "\'" +PAN+"\'" + "," + "\'" + 4 + "\'" +")")
        $("#biaoji1").css("display","none");
})
}
    })
}

// Change nickname
function modifyNickname(s,yuan) {
    var newNickname = $.trim($(s).parent().prev().children("input").val());
    if (newNickname === yuan) {
        return false
    }
    else if (newNickname.length>30){
        bootbox.alert({title: "Error Alert", message: "The intimate length to be modified exceeds the limit, please modify"});
        return false
    }
    bootbox.confirm({
        title: "Operation Tips",
        message: "Are you sure to change your nickname",
        buttons: {
            cancel: {
                label: 'Reconsider'
            },
            confirm: {
                label: 'Determine the modification'
            }
        },
        callback: function (result) {
            if (result.toString() === "true") {
                $.post("/modifyNickname",param="newNickname="+newNickname,function (data) {
                    if(data==="1"){
                        qingti("Change nickname successfully")
                        $(s).parent().prev().children("input").attr("value", newNickname)
                        $(s).parent().prev().children("input").focus()
                    }
                    else {
                         bootbox.alert({title: "Error Alert", message: "Nickname change failed, please contact the administrator"});
                    }

                })
            }
        }

    })
}

// Apply to become an editor
 function applyEditor(s){
    bootbox.confirm({
        title: "Operation Tips",
        message: "Whether to apply to become an editor, after the consent of the administrator, the editor can publish articles directly without the review of the administrator",
        buttons: {
            cancel: {
                label: 'Reconsider'
            },
            confirm: {
                label: 'Determine the application'
            }
        },
        callback: function (result) {
            if (result.toString() === "true") {
                $.post("/applyEditor",function (data){
                    if (data==="1"){
                        bootbox.alert({title: "Operation Tips", message: "Application is successful, please wait for the administrator's review"});
                        $(s).text("Applied for")
                    }
                })
            }
        }

    })
 }

// Modify qq number
 function modifyQQ(s,yuan) {
    var newQQ = $.trim($(s).parent().prev().children("input").val());
    var reg = new RegExp("^[0-9]*$");
    if (newQQ === yuan) {
        return false
    }
    else if (newQQ.length>11||!reg.test(newQQ)){
        bootbox.alert({title: "Error Alert", message: "QQ number format error, please try again"});
        return false
    }
    bootbox.confirm({
        title: "Operation Tips",
        message: "Are you sure to modify your QQ",
        buttons: {
            cancel: {
                label: 'Reconsider'
            },
            confirm: {
                label: 'Determine the modification'
            }
        },
        callback: function (result) {
            if (result.toString() === "true") {
                $.post("/modifyQQ",param="newQQ="+newQQ,function (data) {
                    if(data==="1"){
                        qingti("Modify QQ successfully")
                        $(s).parent().prev().children("input").attr("value", newQQ)
                        $(s).parent().prev().children("input").focus()
                    }
                    else {
                         bootbox.alert({title: "Error Alert", message: "Modify QQ failure, please contact the administrator"});
                    }

                })
            }
        }

    })
}

// Delete article
 function hideArticle(articleid){
    bootbox.confirm({
        title: "Operation Tips",
        message: "Is it OK to permanently delete the article",
        buttons: {
            cancel: {
                label: 'Reconsider'
            },
            confirm: {
                label: 'OK to delete'
            }
        },
        callback: function (result) {
            if (result.toString() === "true") {
                $.post("/hideArticle",param="articleid="+articleid,function (data) {
                    if(data==="1"){
                        qingti("Delete article successfully")
                        var lin="#article__"+articleid
                        $(lin).css("display","none")
                        var num= $("#allMyArticleNum").text()
                        var newNum=parseInt(num)-1
                        $("#allMyArticleNum").text(newNum)

                    }
                    else {
                         bootbox.alert({title: "Error Alert", message: "Delete article failed, please contact the administrator"});
                    }

                })
            }
        }

    })
 }

// Change the function of the userManage module
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

// Change the article pagination in the admin page
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

     //Above is the number of pages below the change

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

 // Jump to the specified article
 function tiaoArticle(articleid,n){
    location.href="/article/"+articleid.toString();
    $.post("/controlBiaoNum",param="controlBiaoNum="+n.toString(),function (data){
        return false
    })
 }

 // Cancel Favorites
 function cancel_favorite(articleid,n=-1) {
        $.ajax({
            url: "/favorite/" + articleid,
            type: "delete",
            success: function (data) {
                if (data == "not-login") {
                    bootbox.alert({title: "Error Alert", message: "Please login to this screen first"})
                } else if (data == "cancel-pass") {
                    bootbox.alert({title: "Information Tips", message: "Cancel favorite successfully"})
                    //    Menu name changed to Thank You Collection
                    $(".favorite-btn").html('<span class=\"oi oi-heart \" aria-hidden=\"true\" ></span> Welcome back')
                    //    Cancel the click event of the Favorites button
                    $(".favorite-btn").attr("onclick", "").unbind("click");
                    if(n===-1){
                        return false
                    }
                    else {
                        var lin="#favorite__"+n.toString();
                        $(lin).hide()
                    }

                } else {
                    bootbox.alert({title: "Error Alert", message: "Failed to cancel the collection, please contact the administrator"})
                }
            }
        })
    }



// Add article collection
 function add_favorite(articleid) {
        $.post("/favorite", "articleid=" + articleid, function (data) {
            if (data == "not-login") {
                bootbox.alert({title: "Error Alert", message: "Please login to this screen first"})
            } else if (data == "favorite-pass") {
                bootbox.alert({title: "Information Tips", message: "This article is successfully collected, you can view in my favorites, refresh the page again can choose to cancel the collection"})
                //    Menu name changed to Thank You Collection
                $(".favorite-btn").html('<span class=\"oi oi-heart \" aria-hidden=\"true\" style=\"color: red\"></span> 感谢收藏')
                //    Cancel the click event of the Favorites button
                $(".favorite-btn").attr("onclick", "").unbind("click");
            } else {
                bootbox.alert({title: "Error Alert", message: "Collection failure, please contact the administrator"})
            }
        })
    }

 // Add a comment
 function addCommnet(articleid) {
        var content = $.trim($("#comment").val());
        if (content.length < 5 || content.length > 1000) {
            bootbox.alert({title: "Error Alert", message: "Comments are between 5~1000 words"});
            return false
        }
        var param = "articleid=" + articleid + "&content=" + content;
        $.post("/comment", param, function (data) {
            if (data == "not-login") {
                bootbox.alert({title: "Error Alert", message: "Please login before commenting"});
            } else if (data == "add-limit") {
                bootbox.alert({title: "Error Alert", message: "You can only comment up to five times that day"});

            } else if (data == "add-pass") {
                $.get("/toTransmitParam",function (data){
                    var replyAndAddCommentCredit=data["replyAndAddCommentCredit"]
                qingti("Reply to comments successfully, points+"+replyAndAddCommentCredit)
                setTimeout("location.reload();", 2000)

    })


            } else {
                bootbox.alert({title: "Error Alert", message: "There was an error posting a comment, please contact the administrator"});

            }
        })
    }

 // Filling comments (front-end filling)
 function fillComment(articleid, pageid) {
        $("#commentDiv").empty();  // Clear existing comments
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
                    content += 'Reply</label>&nbsp;&nbsp;&nbsp;'
                    content += `<label onclick="hideComment(this,${comment[i]['commentid']},1,${i},-1)"`;

                    content += '<span class="oi oi-delete"aria-hidden="true"></span>Delete Comments</label> ';
                } else {
                    if (comment[i]["agreeOrdisAgreeType"] === 0) {
                        content += `<label onclick="gotoReply(${comment[i]['commentid']})">
                                            <span class="oi oi-arrow-circle-right" aria-hidden="true"></span>Reply
                                        </label>&nbsp;&nbsp;

                                        <label onclick="agreeComment(this,${comment[i]["commentid"]},${comment[i]["agreecount"]})" style="visibility: visible;" id="agreeComment1">
                                            <span class="oi oi-chevron-bottom"
                                                  aria-hidden="true"></span><font>赞成(<span>${comment[i]["agreecount"]}</span>)</font>
                                        </label>&nbsp;&nbsp;

                                        <label onclick="opposeComment(this,${comment[i]["commentid"]},${comment[i]["opposecount"]})" style="visibility: visible;" id="opposeComment1">
                                <font color=""><span class="oi oi-x"
                                      aria-hidden="true"></span>Against(<span>${comment[i]["opposecount"]}</span>)</font>
                                        </label>`
                    } else if (comment[i]["agreeOrdisAgreeType"] === 1) {
                        content += `<label onclick="gotoReply(${comment[i]['commentid']})">
                                            <span class="oi oi-arrow-circle-right" aria-hidden="true"></span>Reply
                                        </label>&nbsp;&nbsp;

                                        <label onclick="cancle_agreeComment(this,${comment[i]["commentid"]},${comment[i]["agreecount"]})" style="visibility: visible;" id="agreeComment1">
                                            <span class="oi oi-chevron-bottom"
                                                  aria-hidden="true"></span><font color="red">Cancel Favor(<span>${comment[i]["agreecount"]}</span>)</font>
                                        </label>&nbsp;&nbsp;

                                        <label onclick="opposeComment(this,${comment[i]["commentid"]},${comment[i]["opposecount"]})" style="visibility: hidden;" id="opposeComment1">
                                <font color=""><span class="oi oi-x"
                                      aria-hidden="true"></span>Against(<span>${comment[i]["opposecount"]}</span>)</font>
                                        </label>`
                    } else if (comment[i]["agreeOrdisAgreeType"] === -1) {
                        content += `<label onclick="gotoReply(${comment[i]['commentid']})">
                                            <span class="oi oi-arrow-circle-right" aria-hidden="true"></span>Reply
                                        </label>&nbsp;&nbsp;

                                        <label onclick="agreeComment(this,${comment[i]["commentid"]},${comment[i]["agreecount"]})" style="visibility: hidden;" id="agreeComment1">
                                            <span class="oi oi-chevron-bottom"
                                                  aria-hidden="true"></span><font>Agree(<span>${comment[i]["agreecount"]}</span>)</font>
                                        </label>&nbsp;&nbsp;

                                        <label onclick="cancle_opposeComment(this,${comment[i]["commentid"]},${comment[i]["opposecount"]})" style="visibility: hidden id="opposeComment1">
                                <font color="red"><span class="oi oi-x"
                                      aria-hidden="true"></span>Cancel Objections(<span>${comment[i]["opposecount"]}</span>)</font>
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

                //    Fill in the reply comments below the current comment
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

                        //    Populate user nickname
                        content += reply[j]["nickname"]
                        content += "Reply";
                        content += comment[i]["nickname"];
                        content += '&nbsp;&nbsp;&nbsp;';
                        content += reply[j]["createtime"];
                        content += '</div>';
                        content += '<div class="col-sm-5 col-12 reply">';

                        //    Replying comments can not continue to comment, but you can delete comments and likes (in the words of the author or administrator)
                        if ("{{article.userid}}" == "{{session.get('userid')}}" ||
                            "{{session.get('role')}}" == "admin" || reply[j]["userid"] + "" == "{{session.get('userid')}}") {
                            content += `<label onclick="hideComment(this,${reply[j]["commentid"]},2,${i},${j})">`;
                            content += '<span class="oi oi-delete" aria-hideen="true"></span>Delete Comments';
                            content += '</label>&nbsp;&nbsp;';
                        }
                        if (comment[i]["agreeOrdisAgreeType"] === 0) {
                            content += `<label onclick="agreeComment(this,${comment[i]["commentid"]},${comment[i]["agreecount"]})" style="visibility: visible;" id="agreeComment1">
                                            <span class="oi oi-chevron-bottom"
                                                  aria-hidden="true"></span><font>赞成(<span>${comment[i]["agreecount"]}</span>)</font>
                                        </label>&nbsp;&nbsp;

                                        <label onclick="opposeComment(this,${comment[i]["commentid"]},${comment[i]["opposecount"]})" style="visibility: visible;" id="opposeComment1">
                                <font color=""><span class="oi oi-x"
                                      aria-hidden="true"></span>Against(<span>${comment[i]["opposecount"]}</span>)</font>
                                        </label>`
                        } else if (comment[i]["agreeOrdisAgreeType"] === 1) {
                            content += `<label onclick="cancle_agreeComment(this,${comment[i]["commentid"]},${comment[i]["agreecount"]})" style="visibility: visible;" id="agreeComment1">
                                            <span class="oi oi-chevron-bottom"
                                                  aria-hidden="true"></span><font color="red">Cancel Favor(<span>${comment[i]["agreecount"]}</span>)</font>
                                        </label>&nbsp;&nbsp;

                                        <label onclick="opposeComment(this,${comment[i]["commentid"]},${comment[i]["opposecount"]})" style="visibility: hidden;"  id="opposeComment1">
                                <font color=""><span class="oi oi-x"
                                      aria-hidden="true"></span>Against(<span>${comment[i]["opposecount"]}</span>)</font>
                                        </label>`
                        } else if (comment[i]["agreeOrdisAgreeType"] === -1) {
                            content += `<label onclick="agreeComment(this,${comment[i]["commentid"]},${comment[i]["agreecount"]})" style="visibility: hidden;" id="agreeComment1">
                                            <span class="oi oi-chevron-bottom"
                                                  aria-hidden="true"></span><font>Agree(<span>${comment[i]["agreecount"]}</span>)</font>
                                        </label>&nbsp;&nbsp;
                                        <label onclick="cancle_opposeComment(this,${comment[i]["commentid"]},${comment[i]["opposecount"]})" style="visibility:visible;" id="opposeComment1">
                                <font color="red"><span class="oi oi-x"
                                      aria-hidden="true"></span>Cancel Objections(<span>${comment[i]["opposecount"]}</span>)</font>
                                        </label>`
                        }

                        content += '</div>';
                        content += '</div>';
                        content += '<div class="col-12">';
                        content += 'Reply content' + reply[j]["content"];
                        content += '</div>';
                        content += '</div>';
                        content += '</div>';


                    }
                }
            }
            $("#commentDiv").html(content);  //Fill in the comment section

        });
    }

 //  Reply to original comment
 function replyComment(articleid) {
        var content = $.trim($("#comment").val());
        if (content.length < 5 || content.length > 1000) {
            bootbox.alert({title: "Error Alert", message: "Comment content between 5~1000 words again"});
            return false
        }
        var param = "articleid=" + articleid;
        param += "&content=" + content;
        param += "&commentid=" + COMMENTID;
        $.post("/reply", param, function (data) {
            if (data == "not-login") {
                bootbox.alert({title: "Error Alert", message: "Please login first"});
            } else if (data == "reply-limit") {
                bootbox.alert({title: "Error Alert", message: "Number of times comments have been used up for the day"});
            } else if (data == "reply-pass") {
                $.get("/replyAndAddCommentCredit",function (data){
                    var replyAndAddCommentCredit=data["replyAndAddCommentCredit"]
                qingti("Reply to comments successfully, points+"+replyAndAddCommentCredit)
                setTimeout("location.reload();", 2000)

    })
                gotoPage(articleid,PAGE)

            } else if (data == "reply-fail") {
                bootbox.alert({title: "Error Alert", message: "Reply to a comment error, please contact the administrator"});
            }
        })

    }

 // Add a comment to the article
 function gotoReply(commentid) {
        $("#replyBtn").show();
        $("#submitBtn").hide();
        if ("{{session.get('islogin')}}" === "true") {
            $("#nickname_1").val("Please reply here with the number" + commentid + "Comments");
        } else {
            $("#nickname_2").val("Please reply here with the number" + commentid + "Comments");
        }

        $("#comment").focus();
        COMMENTID = commentid;

    }

 // Comments jump to which page
 function gotoPage(articleid, type) {
        //    If the current page is the first page, then the previous page is still the first page
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

// Define the search function
function dosearch(e) {
        if (e != null && e.keyCode != 13) {
            return false
        }
        var keyword = $.trim($("#keyword").val());
        if (keyword.length === 0 || keyword.length > 10 || keyword.indexOf("%") >= 0) {
            bootbox.alert({"title": "Error Alert", "message": "The keyword you entered is not legal"});
            $("#keyword").focus();
            return false
        }
        location.href = "/search/1-" + keyword;
    }

// Intercept string
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

//   Define a function to delete multiple articles
function delMany(){
				var names=document.getElementsByName("checkbox[]");
                var arr=[]
                bootbox.confirm({
        title: "Operation Tips",
        message: "Is it OK to delete the article",
        buttons: {
            cancel: {
                label: 'Reconsider'
            },
            confirm: {
                label: 'Determine the modification'
            }
        },
        callback: function (result) {
            if (result.toString() === "true") {
                for(var x=0;x<names.length;x++){
					if(names[x].checked){//Add up all the selected ones
						arr.push(parseInt(names[x].value));//Add the selected values to a list

					}
				}
                for (const w of arr) {

        $.post("/hideArticle",param="articleid="+w.toString(),function (data) {
                    if(data==="1"){
                        return false
                    }
                    else {
                         bootbox.alert({title: "Error Alert", message: "Delete article failed, please contact the administrator"});
                    }

                })


    }
                $.post("/controlBiaoNum",param="controlBiaoNum="+"1",function (data){
                    if (data==="1"){
                        qingti("Delete article successfully")
                bootbox.alert({title: "Operation Tips", message: "Delete article successfully"});
                setTimeout(function (){location.reload()}, 1000)
                    }
                    else {
                        bootbox.alert({title: "Operation Tips", message: "Delete article failed, please contact the administrator"});
                    }

                })





            }
        }

    })



			}




