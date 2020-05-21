flectra.define('MarketingAutomation.dashboard', function (require) {
    'use strict';

    var core = require('web.core');
    var QWeb = core.qweb;
    var Widget = require('web.Widget');
    var ajax = require('web.ajax');
    var datepicker = require('web.datepicker');
    var ControlPanelMixin = require('web.ControlPanelMixin');

    var dashboard = Widget.extend(ControlPanelMixin, {
        template: 'MarketingAutomation.dashboard',
        cssLibs: [
            '/web/static/lib/nvd3/nv.d3.css'
        ],
        jsLibs: [
            '/web/static/lib/nvd3/d3.v3.js',
            '/web/static/lib/nvd3/nv.d3.js',
            '/web/static/src/js/libs/nvd3.js'
        ],
        init: function () {
            this._super.apply(this, arguments);
        },
        willStart: function () {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super()).then(function () {
                return self.fetch_data();
            });
        },
        fetch_data: function () {
            var self = this;
            return $.when(self.fetchAllCampaign(),
                self.fetchMailCampaignStatisticsRatio(),
                self.fetchMailCampaignStatistics());
        },
        fetchMailCampaignStatisticsRatio: function (id) {
            var self = this;
            var filter = id ? parseInt(id) : null;
            return self._rpc({
                model: 'mail.marketing',
                method: 'get_marketing_stats_ratio',
                args: [[], filter]
            }).done(function (res) {
                var overall_statistics = res['overall_statistics'];
                var results_per_campaign = res['results_per_campaign'];
                var length = Object.keys(overall_statistics).length;
                var sent_ratio = 0, opened_ration = 0, clicked_ratio = 0,
                    bounced_ratio = 0, replied_ratio = 0, exception_ratio = 0;
                if (length) {
                    _.each(overall_statistics, function (e) {
                        sent_ratio += e[0].sent_ratio;
                        opened_ration += e[0].opened_ration;
                        clicked_ratio += e[0].clicked_ratio;
                        bounced_ratio += e[0].bounced_ratio;
                        replied_ratio += e[0].replied_ratio;
                        exception_ratio += e[0].exception_ratio;
                    });
                    self.sent_ratio = sent_ratio / length;
                    self.opened_ration = opened_ration / length;
                    self.clicked_ratio = clicked_ratio / length;
                    self.bounced_ratio = bounced_ratio / length;
                    self.replied_ratio = replied_ratio / length;
                    self.exception_ratio = exception_ratio / length;
                }
                self.filterTopPerformingEmails(results_per_campaign);
            })
        },
        filterTopPerformingEmails: function (emails) {
            var self = this;
            var all_emails = [];
            _.each(emails, function (e) {
                all_emails.push(e);
            });
            var flatArray = [].concat.apply([], all_emails);
            flatArray.sort(function (a, b) {
                return a["sent"] - b["sent"] || a["opened"] - b["opened"];
            });
            flatArray = flatArray.reverse().slice(0, 5);
            self.top_performing_email = flatArray;
        },
        fetchMailCampaignStatistics: function (id, from_date, to_date) {
            var self = this;
            var filter = id ? parseInt(id) : null;
            return self._rpc({
                model: 'mail.marketing',
                method: 'get_marketing_stats',
                args: [[], filter, from_date, to_date]
            }).done(function (res) {
                self.data = res;
            })
        },
        fetchAllCampaign: function () {
            var self = this;
            return self._rpc({
                model: 'mail.marketing',
                method: 'search_read',
                args: [[]]
            }).done(function (resp) {
                self.mail_marketing = resp;
            })
        },
        start: function () {
            var self = this;
            return this._super().then(function () {
                self.update_cp();
                self.render_radial_progress();
                self.render_line_chart();
            });
        },
        do_show: function () {
            this._super.apply(this, arguments);
            this.update_cp();
        },
        update_cp: function () {
            if (!this.$searchview) {
                this.$searchview = $(QWeb.render("MarketingAutomation.Filters", {
                    widget: this
                }));
            }
            this.update_control_panel({
                breadcrumbs: this.getParent().get_breadcrumbs(),
                cp_content: {
                    $searchview_buttons: this.$searchview
                }
            }, {clear: true});
            this.register_searchview_buttons();
        },

        filterCamp: function (a, filter) {
            for (var i = 0; i < a.length; i++) {
                if (filter == '*') {
                    a[i].style.display = "";
                }
                else {
                    if (a[i].innerHTML.toUpperCase().indexOf(filter) > -1) {
                        a[i].style.display = "";
                    } else {
                        a[i].style.display = "none";
                    }
                }
            }
        },
        register_searchview_buttons: function () {
            var self = this;
            self.$searchview.find('#search_campaign').keyup(function (ev) {
                var filter, a;
                var div = self.$searchview.find('#camp_filters')[0];
                filter = ev.currentTarget.value.toUpperCase();
                a = div.getElementsByTagName("a");
                self.filterCamp(a, filter);
            });
            self.$searchview.find('.js_campaign_filter').click(function (ev) {
                self.$searchview.find('#search_campaign').val('');
                var a = self.$searchview.find('#camp_filters')[0]
                    .getElementsByTagName("a");
                self.filterCamp(a, '*');

                var $target = $(ev.currentTarget);
                var parent = $target.parents('div.o_dropdown.open');
                var id = $target.attr('data-id');
                var progress_data = self.fetchMailCampaignStatisticsRatio(id);
                var line_data = self.fetchMailCampaignStatistics(id);
                $.when(progress_data, line_data).done(function () {
                    parent.find('li').removeClass('selected');
                    parent.removeClass('open');
                    $target.addClass('selected');
                    self.render_radial_progress();
                    self.render_line_chart();
                });
            });
            self.register_date_plugins();
        },
        register_date_plugins: function () {
            var self = this;
            var $datepicker = self.$searchview.find('.o_datepicker_input');
            var options = {
                locale: moment.locale(),
                format: 'L',
                icons: {
                    date: "fa fa-calendar",
                }
            };
            $datepicker.each(function () {
                $(this).datetimepicker(options);
                var dt = new datepicker.DateWidget(options);
                dt.replace($(this));
                dt.$el.find('input').attr('name', $(this).find('input').attr('name'));
                if ($(this).data('default-value')) {
                    dt.setValue(moment($(this).data('default-value')));
                }
            });

            self.$searchview.find('#custom_date').click(function (ev) {
                var from_date = self.$searchview.find('input.o_datepicker_input.o_input')[0].value,
                    to_date = self.$searchview.find('input.o_datepicker_input.o_input')[1].value;
                var $target = $(ev.currentTarget);
                var parent = $target.parents('div.o_dropdown.open');
                var id = self.$searchview.find('.js_campaign_filter.selected').attr('data-id');
                var line_data = self.fetchMailCampaignStatistics(id, from_date, to_date);
                $.when(line_data).done(function () {
                    parent.removeClass('open');
                    self.render_line_chart();
                });
            });
        },
        render_radial_progress: function () {
            var self = this;
            var dashboard_element = $(QWeb.render('MarketingAutomation.marketing_progress', {
                widget: self
            }));
            if (self.$el.find('.marketing-progress').length) {
                self.$el.find('.marketing-progress').replaceWith(dashboard_element);
            } else {
                self.$el.find('.marketing-dashboard').append(dashboard_element);
            }
            var wrappers = self.$el.find('.radial-progress');
            _.each(wrappers, function (el) {
                var start = 0;
                var wrapper = $(el);
                var end = parseFloat(wrapper.attr('data-percentage'));
                var colours = {
                    fill: '#' + wrapper.attr('data-fill-colour'),
                    track: '#' + wrapper.attr('data-track-colour'),
                    text: '#' + wrapper.attr('data-text-colour'),
                    stroke: '#' + wrapper.attr('data-stroke-colour'),
                };
                var radius = 60;
                var border = wrapper.attr('data-track-width');
                var strokeSpacing = wrapper.attr('data-stroke-spacing');
                var endAngle = Math.PI * 2;
                var formatText = d3.format('.0%');
                var boxSize = radius * 2;
                var count = end;
                var progress = start;
                var step = end < start ? -0.01 : 0.01;

                //Define the circle
                var circle = d3.svg.arc()
                    .startAngle(0)
                    .innerRadius(radius)
                    .outerRadius(radius - border);

                //setup SVG wrapper
                var svg = d3.select(wrapper[0])
                    .append('svg')
                    .attr('width', boxSize)
                    .attr('height', boxSize);

                // ADD Group container
                var g = svg.append('g')
                    .attr('transform', 'translate(' + boxSize / 2 + ',' + boxSize / 2 + ')');

                //Setup track
                var track = g.append('g').attr('class', 'radial-progress');
                track.append('path')
                    .attr('class', 'radial-progress__background')
                    .attr('fill', colours.track)
                    .attr('stroke', colours.stroke)
                    .attr('stroke-width', strokeSpacing + 'px')
                    .attr('d', circle.endAngle(endAngle));

                //Add colour fill
                var value = track.append('path')
                    .attr('class', 'radial-progress__value')
                    .attr('fill', colours.fill)
                    .attr('stroke', colours.stroke)
                    .attr('stroke-width', strokeSpacing + 'px');

                //Add text value
                var numberText = track.append('text')
                    .attr('class', 'radial-progress__text')
                    .attr('fill', colours.text)
                    .attr('text-anchor', 'middle')
                    .attr('dy', '.5rem');

                function update(progress) {
                    //update position of endAngle
                    value.attr('d', circle.endAngle(endAngle * progress));
                    //update text value
                    numberText.text(formatText(progress));
                }

                (function iterate() {
                    //call update to begin animation
                    update(progress);
                    if (count > 0) {
                        //reduce count till it reaches 0
                        count--;
                        //increase progress
                        progress += step;
                        //Control the speed of the fill
                        setTimeout(iterate, 10);
                    }
                })();
            })
        },

        render_line_chart: function () {
            var self = this;
            var dashboard_element = $(QWeb.render('MarketingAutomation.line_graph', {
                widget: self
            }));
            if (self.$el.find('.marketing-line-graph').length) {
                self.$el.find('.marketing-line-graph').replaceWith(dashboard_element);
            } else {
                self.$el.find('.marketing-dashboard').append(dashboard_element);
            }
            var Data = self.data;
            // Calling function
            self.fnDrawMultiLineChart(Data, "line_chart_mar", "");
        },

        fnDrawMultiLineChart: function (Data, DivID, RevenueName) {
            var data = Data;
            data.sort(function (a, b) {
                var dateA = new Date(a.date), dateB = new Date(b.date);
                return dateA - dateB;
            });
            var margin = {
                    top: 20,
                    right: 80,
                    bottom: 30,
                    left: 50
                },
                width = 480 - (margin.left - margin.right),
                height = 300 - (margin.top - margin.bottom);

            var parseDate = d3.time.format("%Y-%m-%d").parse;
            var x = d3.time.scale()
                .range([0, width]);

            var y = d3.scale.linear()
                .range([height, 0]);
            var color = d3.scale.category10();

            var xAxis = d3.svg.axis()
                .scale(x)
                .ticks(5)
                .orient("bottom");

            var yAxis = d3.svg.axis()
                .scale(y)
                .orient("left");
            var line = d3.svg.line()
                .interpolate("basis")
                .x(function (d) {
                    return x(d.date);
                })
                .y(function (d) {
                    return y(d.temperature);
                });

            var svg = d3.select(this.$el.find('#' + DivID)[0])
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


            color.domain(d3.keys(data[0]).filter(function (key) {
                return key !== "date";
            }));

            data.forEach(function (d) {
                d.date = parseDate(d.date);
            });

            var emails = color.domain().map(function (name) {
                return {
                    name: name,
                    values: data.map(function (d) {
                        return {
                            date: d.date,
                            temperature: +d[name]
                        };
                    })
                };
            });

            x.domain(d3.extent(data, function (d) {
                return d.date;
            }));

            y.domain([
                d3.min(emails, function (c) {
                    return d3.min(c.values, function (v) {
                        return v.temperature;
                    });
                }),
                d3.max(emails, function (c) {
                    return d3.max(c.values, function (v) {
                        return v.temperature;
                    });
                })
            ]);

            var legend = svg.selectAll('g')
                .data(emails)
                .enter()
                .append('g')
                .attr('class', 'legend');

            legend.append('rect')
                .attr('x', width + 5)
                .attr('y', function (d, i) {
                    return i * 20;
                })
                .attr('width', 10)
                .attr('height', 10)
                .style('fill', function (d) {
                    return color(d.name);
                });

            legend.append('text')
                .attr('x', width + 20)
                .attr('y', function (d, i) {
                    return (i * 20) + 9;
                })
                .text(function (d) {
                    return d.name;
                });

            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);

            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis)
                .append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", ".71em")
                .style("text-anchor", "end")
                .text(RevenueName);

            var email = svg.selectAll(".email")
                .data(emails)
                .enter().append("g")
                .attr("class", "email");

            email.append("path")
                .attr("class", "line")
                .attr("d", function (d) {
                    return line(d.values);
                })
                .style("stroke", function (d) {
                    return color(d.name);
                });

            this.animate_paths(email);
            this.registerMouseListener(svg, emails, width, height, color, x, y);
        },

        animate_paths: function (email) {
            _.each(email[0], function (e, i) {
                var totalLength = $(e).find('path')[0].getTotalLength();
                d3.select(e)
                    .attr("stroke-dasharray", totalLength + " " + totalLength)
                    .attr("stroke-dashoffset", totalLength)
                    .transition()
                    .duration(1000)
                    .ease("linear")
                    .attr("stroke-dashoffset", 0);
            });
        },

        registerMouseListener: function (svg, emails, width, height, color, x, y) {
            var mouseG = svg.append("g")
                .attr("class", "mouse-over-effects");

            mouseG.append("path") // this is the black vertical line to follow mouse
                .attr("class", "mouse-line")
                .style("stroke", "black")
                .style("stroke-width", "1px")
                .style("opacity", "0");

            var lines = document.getElementsByClassName('line');

            var mousePerLine = mouseG.selectAll('.mouse-per-line')
                .data(emails)
                .enter()
                .append("g")
                .attr("class", "mouse-per-line");

            mousePerLine.append("circle")
                .attr("r", 7)
                .style("stroke", function (d) {
                    return color(d.name);
                })
                .style("fill", "none")
                .style("stroke-width", "1px")
                .style("opacity", "0");

            mousePerLine.append("text")
                .attr("transform", "translate(10,3)");

            mouseG.append('svg:rect') // append a rect to catch mouse movements on canvas
                .attr('width', width) // can't catch mouse events on a g element
                .attr('height', height)
                .attr('fill', 'none')
                .attr('pointer-events', 'all')
                .on('mouseout', function () { // on mouse out hide line, circles and text
                    d3.select(".mouse-line")
                        .style("opacity", "0");
                    d3.selectAll(".mouse-per-line circle")
                        .style("opacity", "0");
                    d3.selectAll(".mouse-per-line text")
                        .style("opacity", "0");
                })
                .on('mouseover', function () { // on mouse in show line, circles and text
                    d3.select(".mouse-line")
                        .style("opacity", "1");
                    d3.selectAll(".mouse-per-line circle")
                        .style("opacity", "1");
                    d3.selectAll(".mouse-per-line text")
                        .style("opacity", "1");
                })
                .on('mousemove', function () { // mouse moving over canvas
                    var mouse = d3.mouse(this);
                    d3.select(".mouse-line")
                        .attr("d", function () {
                            var d = "M" + mouse[0] + "," + height;
                            d += " " + mouse[0] + "," + 0;
                            return d;
                        });

                    d3.selectAll(".mouse-per-line")
                        .attr("transform", function (d, i) {
                            var xDate = x.invert(mouse[0]),
                                bisect = d3.bisector(function (d) {
                                    return d.date;
                                }).right;
                            var idx = bisect(d.values, xDate);

                            var beginning = 0,
                                end = lines[i].getTotalLength(),
                                target = null;

                            while (true) {
                                target = Math.floor((beginning + end) / 2);
                                var pos = lines[i].getPointAtLength(target);
                                if ((target === end || target === beginning) && pos.x !== mouse[0]) {
                                    break;
                                }
                                if (pos.x > mouse[0]) end = target;
                                else if (pos.x < mouse[0]) beginning = target;
                                else break; //position found
                            }

                            d3.select(this).select('text')
                                .text(y.invert(pos.y).toFixed(2));

                            return "translate(" + mouse[0] + "," + pos.y + ")";
                        });
                });
        }
    });

    core.action_registry.add('marketing_dashboard', dashboard);

    return dashboard;
});