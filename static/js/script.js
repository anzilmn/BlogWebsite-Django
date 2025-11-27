$(document).ready(function () {
    $("#hamburger-icon").click(function () {
        $("#hamburger-menu").addClass("active");
        $("#overlay").addClass("active");
        $("#close").addClass("active");
    });

    $("#close").click(function () {
        $("#hamburger-menu").removeClass("active");
        $("#overlay").removeClass("active");
        $("#close").removeClass("active");
    });

    $("#overlay").click(function () {
        $("#hamburger-menu").removeClass("active");
        $("#overlay").removeClass("active");
        $("#close").removeClass("active");
    });

    $("a.copy-link").click(function (e) {
        e.preventDefault();
        console.log(window.location.href);
        navigator.clipboard.writeText(window.location.href);
    });
});

$(document).on("click", ".action-button", function (e) {
    e.preventDefault();
    $this = $(this);
    var text = $this.attr("data-text");
    var type = "warning";
    var confirmButtonText = "Yes";
    var confirmButtonColor = "#DD6B55";
    var url = $this.attr("href");
    var title = $this.attr("data-title");
    if (!title) {
        title = "Are you sure?";
    }
    var isReload = $this.hasClass("reload");
    var isRedirect = $this.hasClass("redirect");
    var noResponsePopup = $this.hasClass("no-response-popup");

    Swal.fire({
        title: title,
        text: text,
        icon: type,
        showCancelButton: true,
        confirmButtonText: confirmButtonText,
        confirmButtonColor: confirmButtonColor,
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.showLoading();

            window.setTimeout(function () {
                jQuery.ajax({
                    type: "GET",
                    url: url,
                    dataType: "json",
                    success: function (data) {
                        var message = data["message"];
                        var status = data["status"];
                        var redirect = data["redirect"];
                        var redirect_url = data["redirect_url"];
                        var stable = data["stable"];
                        var title = data["title"];

                        Swal.hideLoading();

                        if (status == "success") {
                            if (title) {
                                title = title;
                            } else {
                                title = "Success";
                            }
                            if (!noResponsePopup) {
                                Swal.fire({
                                    icon: "success",
                                    title: title,
                                    text: message,
                                    type: "success",
                                }).then((result) => {
                                    if (stable != "yes") {
                                        if (isRedirect && redirect == "yes") {
                                            window.location.href = redirect_url;
                                        }
                                        if (isReload) {
                                            window.location.reload();
                                        }
                                    }
                                });
                            }
                        } else {
                            if (title) {
                                title = title;
                            } else {
                                title = "An Error Occurred";
                            }

                            Swal.fire(title, message, "error");

                            if (stable != "true") {
                                window.setTimeout(function () {}, 2000);
                            }
                        }
                    },
                    error: function (data) {
                        Swal.hideLoading();

                        var title = "An error occurred";
                        var message =
                            "An error occurred. Please try again later.";
                        Swal.fire(title, message, "error");
                    },
                });
            }, 100);
        }
    });
});

$(document).on("submit", "form.ajax", function(e) {
    e.preventDefault();
    var $this = $(this);

    document.onkeydown = function (evt) {
        return false;
    };

    var url = $this.attr("action");
    var method = $this.attr("method");
    var isReload = $this.hasClass("reload");
    var isRedirect = $this.hasClass("redirect");
    var noLoader = $this.hasClass("no-loader");
    var noPopup = $this.hasClass("no-popup");

    if (!noLoader) {
        Swal.showLoading();
    }

    jQuery.ajax({
        type: method,
        url: url,
        dataType: "json",
        data: new FormData(this),
        cache: false,
        contentType: false,
        processData: false,
        success: function (data) {
            if (!noLoader) {
                Swal.hideLoading();
            }

            var message = data["message"];
            var status = data["status"];
            var title = data["title"];
            var redirect = data["redirect"];
            var redirect_url = data["redirect_url"];
            var stable = data["stable"];

            if (status == "success") {
                if (title) {
                    title = title;
                } else {
                    title = "Success";
                }

                function doAfter() {
                    if (stable != "yes") {
                        console.log(isRedirect);
                        console.log(redirect);
                        if (isRedirect && redirect === "yes") {
                            window.location.href = redirect_url;
                        }
                        if (isReload) {
                            window.location.reload();
                        }
                    }
                }

                if (noPopup) {
                    doAfter();
                } else {
                    Swal.fire({
                        icon: status,
                        title: title,
                        html: message,
                    }).then((result) => {
                        console.log(result.isConfirmed);
                        if (result.isConfirmed) {
                            doAfter();
                        }
                    });
                }
                document.onkeydown = function (evt) {
                    return true;
                };
            } else {
                if (title) {
                    title = title;
                } else {
                    title = "An Error Occurred";
                }

                Swal.fire(title, message, "error");

                if (stable != "true") {
                    window.setTimeout(function () {}, 2000);
                }
                document.onkeydown = function (evt) {
                    return true;
                };
            }
        },
        error: function (data) {
            Swal.hideLoading();

            var title = "An error occurred";
            var message = "An error occurred. Please try again later.";
            document.onkeydown = function (evt) {
                return true;
            };
            Swal.fire(title, message, "error");
        },
    });
});
