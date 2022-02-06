import React from "react";
import * as d3 from "d3";
import Helpers from '../API'
import Row from 'react-bootstrap/Row';

//https://www.d3-graph-gallery.com/graph/stackedarea_basic.html
const LineChart = (input) => {
    //document.getElementById("App-Container").getBoundingClientRect();
    const dimensions = {
        width: input.frame.width,
        height: input.frame.height,
        margin: {
            top: input.frame.margin,
            bottom: input.frame.margin,
            right: input.frame.margin*2,
            left: input.frame.margin*2
        }
    };
    const svgRef = React.useRef(null);
    const {width, height, margin} = dimensions;
    const svgWidth = width + margin.left + margin.right;
    const svgHeight = height + margin.top + margin.bottom;
    //preconfigured data--we should eventually change
    Helpers.RequestData(input.request).then(data => {
        if(false){
            console.log(data);
        }
        var color = d3.scaleOrdinal(d3.schemeCategory10);
        var parseDate = d3.timeParse("%Y-%m");
        var formatDate = d3.timeFormat("%Y-%m-%d");
        color.domain(Object.keys(data[0]).filter(function(key) {
            return key === "total";
          }));      

        data.forEach(function(d) {
            //todo: unhack api to return numbers and currency seperate
            d.total = +d.total.split(" ")[0];
            d.date  = parseDate(d.year+"-"+d.month);
        });

        console.log(data.map(function(d) { return d.total; }))

        var data_for_lines = color.domain().map(function(name) {
            return {
                name: name,
                values: data.map(function(d) {
                    return {
                        date: d.date,
                        total: d.total
                    };
                })
            };
        });

        var x = d3.scaleTime()
                .range([0, width])
                .domain(d3.extent(data, function(d) { return d.date; }))
                .nice();

        var y = d3.scaleLinear()
                .range([height, 0])
                .domain([
                    0,
                    //d3.min(data,function(d)  { return d.total; }), 
                    d3.max(data_for_lines, function(c) {
                        return d3.max(c.values, function(v) {
                          return v.total;
                        });
                      })
                    //d3.max(data, function(d) { return d.total; })
                ]);

        var svg = d3.select("svg")
            .attr("width", svgWidth)
            .attr("height",svgHeight)
            .append("g")
            .attr("transform", 
                "translate(" + margin.left + "," + margin.top + ")");

        var legend = svg.selectAll('g')
            .data(data_for_lines)
            .enter()
            .append('g')
            .attr('class', 'legend');
    
        legend.append('rect')
            .attr('x', width - 20)
            .attr('y', function(d, i) {
                return i * 20;
            })
            .attr('width', 10)
            .attr('height', 10)
            .style('fill', function(d) {
                return color(d.name);
            });

            legend.append('text')
            .attr('x', width - 8)
            .attr('y', function(d, i) {
                return (i * 20) + 9;
            })
            .text(function(d) {
                return d.name;
            });
        
        var div = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);

        var line = d3.line()
            .x(function(d) { return x(d.date); })
            .y(function(d) { return y(d.total); })
            .curve(d3.curveStepAfter);



        // append the rectangles for the bar chart
        /*svg.append("path")
            .data([data_for_lines])
            .attr("class", "line")
           // .attr("d", line);
           .attr("d", function(d) {
            return line(d.values);
          });*/

        svg = svg.selectAll(".amount")
          .data(data_for_lines)
          .enter().append("g")
          .attr("class", "amount");

        svg.append("path")
          .attr("class", "line")
          .attr("d", function(d) {
            return line(d.values);
          })
          .style("stroke", function(d) {
            return color(d.name);
          });

        svg.append("text")
          .datum(function(d) {
            return {
                name: d.name,
                value: d.values[d.values.length - 1]
            };
          })
          .attr("transform", function(d) {
                return "translate(" + x(d.value.date) + "," + y(d.value.total) + ")";
            })
            .attr("x", 3)
            .attr("dy", ".35em")
            .text(function(d) {
                return d.name;
            });



        var xAxis = d3.axisBottom(x);

        svg.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis.ticks(d3.timeMonth,1).tickFormat(formatDate));

        svg.append("g")
            .call(d3.axisLeft(y));

        var mouseG = svg.append("g")
            .attr("class", "mouse-over-effects");

        mouseG.append("path") // this is the black vertical line to follow mouse
            .attr("class", "mouse-line")
            .style("stroke", "black")
            .style("stroke-width", "1px")
            .style("opacity", "0");

        var lines = document.getElementsByClassName('line');

        var mousePerLine = mouseG.selectAll('.mouse-per-line')
            .data(data_for_lines)
            .enter()
            .append("g")
            .attr("class", "mouse-per-line");

        mousePerLine.append("circle")
            .attr("r", 7)
            .style("stroke", function(d) {
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
            .on('mouseover', function() { // on mouse in show line, circles and text
              d3.select(".mouse-line")
                .style("opacity", "1");
              d3.selectAll(".mouse-per-line circle")
                .style("opacity", "1");
              d3.selectAll(".mouse-per-line text")
                .style("opacity", "1");
            })
            .on('mousemove', function(event) { // mouse moving over canvas
              var mouse = d3.pointer(event);

              d3.select(".mouse-line")
                .attr("d", function() {
                  var d = "M" + mouse[0] + "," + height;
                  d += " " + mouse[0] + "," + 0;
                  return d;
                });
      
              d3.selectAll(".mouse-per-line")
                .attr("transform", function(d, i) {
                  var xDate = x.invert(mouse[0]),
                  bisect = d3.bisector(function(d) { return d.date; }).right;
                  var idx = bisect(d.values, xDate);
                  
                  var beginning = 0,
                      end = lines[i].getTotalLength(),
                      target = null;
      
                  while (true){
                    target = Math.floor((beginning + end) / 2);
                    var pos = lines[i].getPointAtLength(target);
                    if ((target === end || target === beginning) && pos.x !== mouse[0]) {
                        break;
                    }
                    if (pos.x > mouse[0])      end = target;
                    else if (pos.x < mouse[0]) beginning = target;
                    else break; //position found
                  }
                  //d3.select(this).select('text')
                  //  .text(y.invert(pos.y).toFixed(2));
                  d3.select(this).select('text')
                    .text(y.invert(pos.y).toFixed(2))
                    .attr("transform", "translate(10,-10)");

                  
                  return "translate(" + mouse[0] + "," + pos.y +")";
                });
            });
    });
    
    return (
        <Row className="g-0" id="module-content">
            <svg ref={svgRef} width={svgWidth} height={svgHeight} />
        </Row>
    );
    
}


export default LineChart