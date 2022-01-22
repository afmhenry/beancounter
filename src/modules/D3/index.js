import React from "react";
import * as d3 from "d3";
import Helpers from '../API'


const BarChart = () => {

    const dimensions = {
        width: 900,
        height: 300,
        margin: {
            top: 30,
            right: 30,
            bottom: 30,
            left: 60
        }
    };
    const svgRef = React.useRef(null);
    const {width, height, margin} = dimensions;
    const svgWidth = width + margin.left + margin.right;
    const svgHeight = width + margin.top + margin.bottom;
    Helpers.RequestData({"Include":"Expenses","Exclude":"Tax", "Month": "12,11,10"}).then(data => {
        var parseDate = d3.timeParse("%Y-%m-%d");
        var formatDate = d3.timeFormat("%b");
        data.forEach(function(d) {
            //todo: unhack api to return numbers and currency seperate
            d.total = +d.total.split(" ")[0];
            d.date  = parseDate(d.date);
        });

        var x = d3.scaleBand()
        .range([0, width])
        .padding(0.1);

        var y = d3.scaleLinear()
                .range([height, 0]);
                
        // append the svg object to the body of the page
        // append a 'group' element to 'svg'
        // moves the 'group' element to the top left margin
        var svg = d3.select("div").append("svg")
            .attr("width", svgWidth)
            .attr("height",svgHeight)
        .append("g")
            .attr("transform", 
                "translate(" + margin.left + "," + margin.top + ")");

        // get the data
        // format the data



        // Scale the range of the data in the domains
        x.domain(data.map(function(d) { return d.date; }));
        
        y.domain([d3.min(data,function(d) { return d.total; }), d3.max(data, function(d) { return d.total; })]);

        // append the rectangles for the bar chart
        svg.selectAll(".bar")
            .data(data)
            .enter().append("rect")
            .attr("class", "bar")
            .attr("x", function(d) { return x(d.date); })
            .attr("width", x.bandwidth())
            .attr("y", function(d) { return y(d.total); })
            .attr("height", function(d) { return height - y(d.total); });

        // add the x Axis
        //todo, make the axis not horrible
        var xAxis = d3.axisBottom(x);

        svg.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);

        // add the y Axis
        svg.append("g")
            .call(d3.axisLeft(y));
    });
    
    return (
        <svg ref={svgRef} width={svgWidth} height={svgHeight} />
        );
    
}

export default BarChart