import React from "react";
import * as d3 from "d3";
import Helpers from '../API'
import Row from 'react-bootstrap/Row';


const LineChart = (input) => {
    //document.getElementById("App-Container").getBoundingClientRect();
    const dimensions = {
        width: 600,
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
    const svgHeight = height + margin.top + margin.bottom;
    //preconfigured data--we should eventually change
    Helpers.RequestData(input).then(data => {
        var parseDate = d3.timeParse("%Y-%m");
        var formatDate = d3.timeFormat("%Y-%m-%d");
        data.forEach(function(d) {
            //todo: unhack api to return numbers and currency seperate
            d.total = +d.total.split(" ")[0];
            d.date  = parseDate(d.year+"-"+d.month);
            console.log(d)
        });

        console.log(data.map(function(d) { return d.date; }))
        var x = d3.scaleTime()
                .range([0, width])
                .domain(d3.extent(data, function(d) { return d.date; }))
                .nice();

        var y = d3.scaleLinear()
                .range([height, 0])
                .domain([
                    0,
                    //d3.min(data,function(d)  { return d.total; }), 
                    d3.max(data, function(d) { return d.total; })
                ]);

        var line = d3.line()
            .x(function(d) { return x(d.date); })
            .y(function(d) { return y(d.total); });

        var svg = d3.select("svg")
            .attr("width", svgWidth)
            .attr("height",svgHeight)
        .append("g")
            .attr("transform", 
                "translate(" + margin.left + "," + margin.top + ")");

        // get the data
        // format the data

        // Scale the range of the data in the domains
        
        

        // append the rectangles for the bar chart
        svg.append("path")
            .data([data])
            .attr("class", "line")
            .attr("d", line);
        /*svg.selectAll(".bar")
            .data(data)
            .enter().append("rect")
            .attr("class", "bar")
            .attr("x", function(d) { return x(d.date); })
            .attr("width", width/data.length-1)
            //.attr("width", x.bandwidth())
            .attr("y", function(d) { return y(d.total); })
            .attr("height", function(d) { return height - y(d.total); });*/

        // add the x Axis
        //todo, make the axis not horrible
        var xAxis = d3.axisBottom(x);

        svg.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis.ticks(d3.timeMonth,1).tickFormat(formatDate));

        // add the y Axis
        svg.append("g")
            .call(d3.axisLeft(y));
    });
    
    return (
        <Row className="g-0" id="module-content">
            <svg ref={svgRef} width={svgWidth} height={svgHeight} />
        </Row>
    );
    
}


export default LineChart