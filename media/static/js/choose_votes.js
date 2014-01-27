ref_url="127.0.0.1:8000"
//ref_url="www.ccu-dev.com"
function loadTopicForm(){
    $('#html_descript').html("<b>Processing...</b>");
    
    var dateVal = $('#dateSelect').val();
    if (dateVal=="choose"){
        dateVal = getDateVals();
        if (dateVal=="error"){
            return;
        }
    }
    //alert(dateVal);

    topicVal = $('#topicSelect').val();
    subtopicVal = "none"
    if ($('#subtopicSelect').val() != null){
        subtopicVal = $('#subtopicSelect').val();
    }    
    strSelect = "none"
    $('#senatorSelect :selected').each(function(i, selected){ 
       if (i==0){
           strSelect = ""
       }
       strSelect = strSelect + '*' + $(selected).val();
       });
    
    
     
    $.ajax( {
          type:'Get',
          url:'http://' + ref_url + '/loadVotesTopic/' + dateVal +'&'+ topicVal + '&' + subtopicVal + '&' + strSelect,
          success:function(data) {
                var i=0;
                var dHTML = data['html_descript'];
                var buildhtml = ""
                for (key in dHTML){
                    buildhtml = buildhtml + '<hr><br>' + dHTML[i] + '<br>';
                    i=i+1;
                }
                $('#html_descript').html(buildhtml)
                if (i==0){
                    $('#html_descript').html('No results for these selections, broaden your search and try again.<br>')
                }
          }});    
}

function loadSenatorForm(){
    $('#html_descript').html("<b>Processing...</b>");
    
    var dateVal = $('#dateSelect').val();

    strSelect = "none"
    $('#senatorSelect :selected').each(function(i, selected){ 
       if (i==0){
           strSelect = ""
       }
       strSelect = strSelect + '*' + $(selected).val();
       });
    
    stateVal = $('#stateSelect').val();
      
    $.ajax( {
          type:'Get',
          url:'http://' + ref_url + '/loadVotesSenator/' + dateVal + '&' + stateVal + '&' + strSelect,
          success:function(data) {
                var i=0;
                var dHTML = data['html_descript'];
                var buildhtml = ""
                for (key in dHTML){
                    buildhtml = buildhtml + '<hr><br>' + dHTML[i] + '<br>';
                    i=i+1;
                }
                $('#html_descript').html(buildhtml)
                if (i==0){
                    $('#html_descript').html('No results for these selections, broaden your search and try again.<br>')
                }
          }});    
}


function loadContrForm(){
    $('#html_descript').html("<b>Processing...</b>");
    var dateVal = $('#dateSelectSector').val();
    if (dateVal=="choose"){
        dateVal = getDateVals();
        if (dateVal=="error"){
            return;
        }
    }

    sectorVal = $('#sectorSelect').val();
    industryVal = $('#industrySelect').val();
    if (industryVal==null){
        industryVal="none"
    }
    businessVal = $('#businessSelect').val();
    if (businessVal==null){
        businessVal="none"
    }
    
    strSelect = "none"
    $('#senatorSelectSector :selected').each(function(i, selected){ 
       if (i==0){
           strSelect = ""
       }
       strSelect = strSelect + '*' + $(selected).val();
       });
    
    
     
    $.ajax( {
          type:'Get',
          url:'http://' + ref_url + '/loadVotesContr/' + dateVal +'&'+ sectorVal + '&' + industryVal + '&' + businessVal + '&' + strSelect,
          success:function(data) {
                //alert(data);
                var i=0;
                var dHTML = data['html_descript'];
                var buildhtml = ""
                for (key in dHTML){
                    buildhtml = buildhtml + '<hr><br>' + dHTML[i] + '<br>';
                    i=i+1;
                }
                $('#html_descript').html(buildhtml)
                if (i==0){
                    $('#html_descript').html('No results for these selections, broaden your search and try again.<br>')
                }
          }});    
}





function populateSenators(strSenators){
    $('#senatorSelect').children().remove();
  
    if (strSenators==""){
        $('#senatorSelect').append('<option value="all">No Senators for this option</option>');
        return;
    }
    $('#senatorSelect').append('<option value="all">All Senators</option>'); 
    $.each(strSenators.split('*'),function(){
        arr = this.split(':');
        $('#senatorSelect').append('<option value="' + arr[0] + '">' + arr[1] + '</option>');    
        
    })   
}

function populateTopics(strTopics){
    $('#subtopicSelect').children().remove();  
       
    $('#topicSelect').children().remove();
    if (strTopics==""){
        $('#topicSelect').append('<option value="all">No Topics for these dates</option>');
        return;
    }
    $('#topicSelect').append('<option value="all">All Topics</option>'); 
    $.each(strTopics.split('*'),function(){
        arr = this.split(':');
        $('#topicSelect').append('<option value="' + arr[0] + '">' + arr[1] + '</option>');    

    })
}

function populateBuses(strTopics){
    $('#businessSelect').append('<option value="all">All Businesses</option>'); 
    $.each(strTopics.split('*'),function(){
        arr = this.split(':');
        $('#businessSelect').append('<option value="' + arr[0] + '">' + arr[1] + '</option>');    

    })
}//end of function



function populateSectors(strTopics){
    
    
    $('#industrySelect').children().remove();
    $('#businessSelect').children().remove();       
    $('#sectorSelect').children().remove();
    
    if (strTopics==""){
        $('#sectorSelect').append('<option value="all">No Sectors for these dates</option>'); 
        return
    }
    
    $('#sectorSelect').append('<option value="all">All Sectors</option>'); 
    $.each(strTopics.split('*'),function(){
        arr = this.split(':');
        $('#sectorSelect').append('<option value="' + arr[0] + '">' + arr[1] + '</option>');    

    })
}

function populateIndustries(strTopics){
    $('#businessSelect').children().remove();   
       
    $('#industrySelect').children().remove();
    $('#industrySelect').append('<option value="all">All Industries</option>'); 
    $.each(strTopics.split('*'),function(){
        arr = this.split(':');
        $('#industrySelect').append('<option value="' + arr[0] + '">' + arr[1] + '</option>');    

    })
}


function populateFromSubtopic(){
    dateVal = $('#dateSelect').val();
    if (dateVal=="choose"){
        dateVal = getDateVals();
        if (dateVal=="error"){
            return;
        }
    }
    topicVal = $('#topicSelect').val();
    subtopicVal = $('#subtopicSelect').val();
    $('#senatorSelect').children().remove();
    $('#senatorSelect').append('<option value="all">Please wait, loading senators....</option>');
   
    $.ajax( {
           type:'Get',
           url:'http://' + ref_url + '/popSelectBoxesSubtopic/' + dateVal + '&' + topicVal + '&' + subtopicVal,
           success:function(data) {   
               var strSenators = data['senators'];
               populateSenators(strSenators);
           }       
       });
    
    
}//end of function

function populateFromState(){
    dateVal = $('#dateSelect').val();
    stateVal = $('#stateSelect').val();
    $('#senatorSelect').children().remove();
    $('#senatorSelect').append('<option value="all">Please wait, loading senators....</option>');
   
    $.ajax( {
           type:'Get',
           url:'http://' + ref_url + '/popSelectBoxesState/' + dateVal + '&' + stateVal,
           success:function(data) {   
               var strSenators = data['senators'];
               populateSenators(strSenators);
           }       
       });
    
    
}//end of function





function getDateVals(){
    var dateVal1 = $('#datepicker').val();
    var dateVal2 = $('#datepicker2').val();
    if (dateVal1=="" || dateVal2==""){
        //alert('Please enter both dates');
        return "error";
    }
    
    if (dateVal1 > dateVal2){
        alert('The first date should be before the second date.')
        return "error";
    }
    dateVal1 = dateVal1.replace(/\//g,'-');
    dateVal2 = dateVal2.replace(/\//g,'-');
    //alert('here in date vals 2');
    
    return dateVal1  + '*' + dateVal2
}

function getDateValsSector(){
    var dateVal1 = $('#datepickerSector').val();
    var dateVal2 = $('#datepickerSector2').val();
    if (dateVal1=="" || dateVal2==""){
        //alert('Please enter both dates');
        return "error";
    }
    
    if (dateVal1 > dateVal2){
        alert('The first date should be before the second date.')
        return "error";
    }
    //alert(dateVal1);
    //alert(dateVal2);
    dateVal1 = dateVal1.replace(/\//g,'-');
    dateVal2 = dateVal2.replace(/\//g,'-');
    //alert('here in date vals 2');
    if (dateVal1=="" || dateVal2==""){
        //alert('Please enter both dates');
        return "error";
    }
    return dateVal1  + '*' + dateVal2
}


function loadFromDatepicker(){
    //alert('here in date picker');
    strDateVal = getDateVals();
    if (strDateVal=="error"){
        return;
    }
    $.ajax( {
        type:'Get',
        url:'http://' + ref_url + '/popSelectBoxes/' + strDateVal,
        success:function(data) {
             var strSenators = data['senators'];
              populateSenators(strSenators);
               //$('#subtopicSelect').css({'width':'200px'});
              var strTopics=data['topics'];
              populateTopics(strTopics);   
        }});
}//end of function



function loadFromTopic(){
    dateVal = $('#dateSelect').val();
    if (dateVal=="choose"){
        dateVal = getDateVals();
        if (dateVal=="error"){
            return;
        }
    }
    topicVal = $('#topicSelect').val();
    
    $.ajax( {
           type:'Get',
           url:'http://' + ref_url + '/popSelectBoxesTopic/' + dateVal + '&' + topicVal,
           success:function(data) {
               var strSenators = data['senators'];
               populateSenators(strSenators);
               
               var strSubTopics = data['subtopics'];
               $('#subtopicSelect').css({'width':'296px'});
               $('#subtopicSelect').children().remove();
               if (topicVal!='all'){
               $('#subtopicSelect').append('<option value="all">All Subtopics</option>'); 
                   $.each(strSubTopics.split('*'),function(){
                           arr = this.split(':');
                           $('#subtopicSelect').append('<option value="' + arr[0] + '">' + arr[1] + '</option>');    

                       })
               }
           }       
       });
    
}//end of loadFromTopic

function loadFromDate(){

    dateVal = $('#dateSelect').val();
    if (dateVal=="choose"){
        $('#hide_div1').show();
        return
    }
    $.ajax( {
        type:'Get',
        url:'http://' + ref_url + '/popSelectBoxes/' + dateVal,
        success:function(data) {
                  $('#hide_div1').hide();    
                  var strSenators = data['senators'];
                  populateSenators(strSenators);
 
                  var strTopics=data['topics'];
                  populateTopics(strTopics);
                    
        }});
}//end of loadFromDate

function loadFromIndustry(){
    dateVal = $('#dateSelectSector').val();
       if (dateVal=="choose"){
           dateVal = getDateValsSector();
           if (dateVal=="error"){
               return;
           }
     }
   indID = $('#industrySelect').val();
   
   $.ajax( {
       type:'Get',
       url:'http://' + ref_url + '/popSelectBoxesBusinesses/' + dateVal +'&'+ indID,
       success:function(data) {
                 
                 var strBuses=data['businesses'];
                 populateBuses(strBuses);
                   
       }});
}//end of function




function loadFromSector(){
    dateVal = $('#dateSelectSector').val();
       if (dateVal=="choose"){
           dateVal = getDateValsSector();
           if (dateVal=="error"){
               return;
           }
     }
   sectorID = $('#sectorSelect').val();
   
   $.ajax( {
       type:'Get',
       url:'http://' + ref_url + '/popSelectBoxesIndustry/' + dateVal +'&'+ sectorID,
       success:function(data) {
               
                 var strIndustries=data['industries'];
                 populateIndustries(strIndustries);
                   
       }});
}//end of function

function loadFromDatepickerSector(){
    strDateVal = getDateValsSector();
    if (strDateVal=="error"){
        return;
    }
    $.ajax( {
        type:'Get',
        url:'http://' + ref_url + '/popSelectBoxesSector/' + strDateVal,
        success:function(data) {
              var strSectors=data['sectors'];
              populateSectors(strSectors);   
        }});
}//end of function



function loadFromDateSector(){
    dateVal = $('#dateSelectSector').val();
    if (dateVal=="choose"){
        $('#hide_div2').show();
        return
    }
    
    
    $.ajax( {
        type:'Get',
        url:'http://' + ref_url + '/popSelectBoxesSector/' + dateVal,
        success:function(data) {
                  $('#hide_div2').hide();
                  var strSectors=data['sectors'];
                  populateSectors(strSectors);
                    
        }});
}//end of loadFromDate
