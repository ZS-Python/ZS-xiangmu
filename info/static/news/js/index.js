var currentCid = 1; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = true;   // 正在向后台获取数据,不能上拉刷新, 为false获取完毕,可以下拉


$(function () {
    // 网页启动完成后,立即主动获取新闻数据列表
    updateNewsData()

    // 首页分类切换
    $('.menu li').click(function () {
        var clickCid = $(this).attr('data-cid')
        $('.menu li').each(function () {
            $(this).removeClass('active')
        })
        $(this).addClass('active')

        if (clickCid != currentCid) {
            // 记录当前分类id
            currentCid = clickCid

            // 重置分页参数
            cur_page = 1
            total_page = 1
            updateNewsData()
        }
    })

    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 100) {
            // TODO 判断页数，去更新新闻数据
            if (!data_querying){
                //加载下一页,同时改成ture
                data_querying = true;
                // 继续加载下一页, 同时cur_page要加1页,(当前页加1)
                cur_page += 1;

                // 判断是否时最后一页
                if (cur_page < total_page){
                    updateNewsData()
                }
            }
        }
    })
})

function updateNewsData() {
    // TODO 更新新闻数据

    var data_dict = {
        'page':cur_page,
        'cid':currentCid
    }

    $.get('/news_list',data_dict,function (response) {
        // 数据加载完,不管数据是否成功失败, 都要把状态改成没有正在加载数据.可以上拉
        data_querying = false;


        if (response.errno == '0'){
            //  响应成功,告诉浏览器一共多少页
            total_page = response.data.total_page

            //   获取数据成功
            for (var i=0;i<response.data.news_dict_list.length;i++) {
                var news = response.data.news_dict_list[i]
                var content = '<li>'
                content += '<a href="#" class="news_pic fl"><img src="' + news.index_image_url + '?imageView2/1/w/170/h/170"></a>'
                content += '<a href="#" class="news_title fl">' + news.title + '</a>'
                content += '<a href="#" class="news_detail fl">' + news.digest + '</a>'
                content += '<div class="author_info fl">'
                content += '<div class="source fl">来源：' + news.source + '</div>'
                content += '<div class="time fl">' + news.create_time + '</div>'
                content += '</div>'
                content += '</li>'
                $(".list_con").append(content)
            }
        }else{
            alert(response.errmsg)
        }
    })
}
