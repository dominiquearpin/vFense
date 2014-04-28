define(
    ['jquery', 'underscore', 'backbone', 'crel', 'modules/lists/pageable', 'text!templates/reports.html',
     'text!templates/osReport.html', 'text!templates/networkReport.html',
     'text!templates/memoryReport.html', 'text!templates/cpuReport.html',
	 'text!templates/hddReport.html', 'text!templates/hardwareReport.html'],
    function ($, _, Backbone, crel, Pager, myTemplate, osReport, networkReport, memoryReport, cpuReport, hddReport, hardwareReport) {

        'use strict';

        var exports = {
            Collection: Pager.Collection.extend({
                baseUrl: 'api/v1/reports/',
                reportType: 'os',
                url: function () {
                    var url = this.baseUrl + this.reportType,
                        query = this.query();
                    if (query !== '?') { url += query; }
                    return url;
                },
                parse: function (response) {
                    return Pager.Collection.prototype.parse.call(this, response);
                }
            }),
            Pager: Pager.View.extend({
                initialize: function (options) {
                    this.collection = new exports.Collection({
                        _defaultParams: {offset: 0, count: 20}
                    });
                    return Pager.View.prototype.initialize.call(this, options);
                },
                reportTemplates: {
                    'os': osReport,
                    'network': networkReport,
                    'memory': memoryReport,
                    'cpu': cpuReport,
                    'disk': hddReport,
					'hardware': hardwareReport
                },
                layoutHeader: function ($left, $right) {
                    var headerTemplate = _.template(this.reportTemplates[this.collection.reportType]);
                    $left.append(headerTemplate({header: true, legend: false, left: true}));
                    $right.append(headerTemplate({header: true, legend: false, left: false, query: this.collection.params}));
                    return this;
                },
                layoutLegend: function ($legend) {
                    var legendTemplate = _.template(this.reportTemplates[this.collection.reportType]);
                    $legend.append(legendTemplate({header: false, legend: true, query: this.collection.params}));
                    return this;
                },
                renderModel: function (model) {
                    var template = _.template(this.reportTemplates[this.collection.reportType]),
                        payload = {
                            header: false,
                            legend: false,
                            params: this.collection.params,
                            model: model,
                            viewHelpers: {
                                getDriveSize: function (size) {
                                    var result = Math.floor(size / 1000000);
                                    if (result) {
                                        return result + ' GB';
                                    } else {
                                        return Math.floor(size / 1000) + ' MB';
                                    }
                                }
                            }
                        };
                    return template(payload);
                }
            }),
            View: Backbone.View.extend({
                initialize: function () {
                    this.pager = new exports.Pager();
                    this.prevSearchType = 'computer_name';
                    return this;
                },
                template: myTemplate,
                events: {
                    'change select[name=advancedSearch]'    : 'filterBySearch',
                    'change select[name=sort]'              : 'sortBy',
                    'change select[name=order]'             : 'orderBy',
                    'change select[name=filterKey]'         : 'filterKeyChange',
                    'change select[name=filterValue]'       : 'filterValueChange',
                    'keyup input[name=search]'              : 'debouncedSearch',
                    'click li a'                            : 'switchTab'
                },
                debouncedSearch: _.debounce(function (event) {
                    var searchType = $(event.currentTarget).data('type');
                    if(this.prevSearchType !== searchType) {
                        delete this.pager.collection.params.key[this.prevSearchType];
                        delete this.pager.collection.params.query;
                        this.prevSearchType = searchType;
                    }
                    this.pager.collection.params.key = this.prevSearchType;
                    this.pager.collection.params.query = $(event.currentTarget).val();
                    this.pager.collection.fetch();
                }, 300),
                filterBySearch: function (event) {
                    var $header = $('header');
                    var $search = $header.find('#searchString');
                    var $selectedElement = $(event.currentTarget).val();
                    if($selectedElement === 'bit_type')
                    {
                        $search.empty();
                        $search.append(crel('div', {class: 'input-prepend noMargin'}, crel('span', {class: 'add-on'}, crel('i', {class: 'icon-search'})), crel('input', {class: 'input-small width-auto', type: 'text', name: 'search', 'data-type': 'bit_type', placeholder: 'Search By System Arch'})));
                    }
                    else if($selectedElement === 'os_string')
                    {
                        $search.empty();
                        $search.append(crel('div', {class: 'input-prepend noMargin'}, crel('span', {class: 'add-on'}, crel('i', {class: 'icon-search'})), crel('input', {class: 'input-small width-auto', type: 'text', name: 'search', 'data-type': 'os_string', placeholder: 'Search By OS String'})));
                    }
                    else if($selectedElement === 'os_code')
                    {
                        $search.empty();
                        $search.append(crel('div', {class: 'input-prepend noMargin'}, crel('span', {class: 'add-on'}, crel('i', {class: 'icon-search'})), crel('input', {class: 'input-small width-auto', type: 'text', name: 'search', 'data-type': 'os_code', placeholder: 'Search By OS Code'})));
                    }
                    else if($selectedElement === 'machine_type')
                    {
                        $search.empty();
                        $search.append(crel('div', {class: 'input-prepend noMargin'}, crel('span', {class: 'add-on'}, crel('i', {class: 'icon-search'})), crel('input', {class: 'input-small width-auto', type: 'text', name: 'search', 'data-type': 'machine_type', placeholder: 'Search By Machine Type'})));
                    }
                    else
                    {
                        $search.empty();
                        $search.append(crel('div', {class: 'input-prepend noMargin'}, crel('span', {class: 'add-on'}, crel('i', {class: 'icon-search'})), crel('input', {class: 'input-small width-auto', type: 'text', name: 'search', 'data-type': 'computer_name', placeholder: 'Search By Computer Name'})));
                    }
                    this.pager.collection.fetch();
                    return this;
                },
                render: function () {
                    var tmpl = _.template(this.template);
                    this.$el.empty().append(tmpl());
                    this.renderContent();
                    return this;
                },
                switchTab: function (event) {
                    event.preventDefault();
                    var $link = $(event.currentTarget),
                        $tab = $link.parent();
                    $tab.addClass('active').siblings().removeClass('active');
                    this.pager.collection.reportType = $link.attr('href');
                    delete this.pager.collection.params.key;
                    delete this.pager.collection.params.query;
                    this.renderContent();
                    return this;
                },
                renderContent: function () {
                    this.pager.render();
                    this.$('.tab-content').empty().append(this.pager.delegateEvents().$el);
                    return this;
                }
            })
        };
        return exports;
    }
);
