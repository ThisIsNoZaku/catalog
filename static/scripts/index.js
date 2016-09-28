var user;
$(document).ready(function(){
	gapi.load('auth2', function(){
		//Delete and update buttons only show for authenticated users.
		if(gapi.auth2.getAuthInstance().isSignedIn.get()){
				user = gapi.auth2.getAuthInstance()currentUser.get();
				$(".authenticated-only").show();
			} else {
				$(".authenticated-only").hide();
			}
		gapi.auth2.getAuthInstance().isSignedIn.listen(function(signedIn){
			if(signedIn){
				user = gapi.auth2.getAuthInstance()currentUser.get();
				$(".authenticated-only").show();
				user = gapi.auth2.getAuthInstance().currentUser.get();
			} else {
				$(".authenticated-only").hide();
			}
		});
	});
	
	var categoryListElement = $("#category-list-element");
	var itemListElement = $("#item-list-element");
	var categories;
	var items;
	var previousCategory;
	var selectedCategory;
	var previousItem;
	var selectedItem;
	
	function setItem(newItem){
		previousItem = selectedItem;
		selectedItem = newItem;
	}
	
	function setCategory(newCategory){
		previousCategory = selectedCategory
		selectedCategory = newCategory
	}
	
	//I replaced a lot of smaller ajax calls with this one.
	function updateSelected(){
		return $.when(
			$.ajax("/items", {
				dataType : "json"
			})
			, 
			$.ajax("/categories", {
				dataType : "json"
			})
		).done(function(returneditems, returnedcategories){
			categories = returnedcategories[0].categories;
			items = returneditems[0].items;
			var hashPairs = window.location.hash.substr(1).split("&").reduce(function(current, next){
				var pair = next.split("=");
				current[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1]);
				return current;
			}, {});
			for(var property in hashPairs){
				switch(property){
					case "category":
						setCategory(categories.find(function(e){
							return e[1] == hashPairs[property];
						})[0]);
						break;
					case "item":
						setItem(items.find(function(e){
							return e[1] == hashPairs[property];
						})[0]);
						break;
				}
			}
		});
	}
	
	//Populate the list of items, either all or filtered by selected category
	function displayItemsList(){
		var container = $("#item-container");
		if(selectedCategory != previousCategory || (selectedCategory === undefined && previousCategory === undefined)){
			container.empty();
			for(var i = 0; i < items.length; i++){
				var newElement = itemListElement.clone(true);
				newElement.find("a").text(items[i][1]);
				newElement.find("a").attr("href", "#item=" + items[i][1]);
				//Capture the index so the handler will have the value at this point in the loop, rather than when the handler fires.
				(function(){
					var index = i;
					newElement.find(".item-delete").data("target", items[index][1]).click(function(){
						var googleUser = gapi.auth2.getAuthInstance().currentUser.get();
						var accessToken = googleUser.Zi.id_token
						$.ajax("/items/" + items[index][0] + "/delete", 
						{
							method : "DELETE",
							headers : {
								"user_id_token" : user.Zi.id_token
							}
						}).fail(function(result){
							console.log(result);
							alert("Something went wrong trying to delete the item.");
						}).done(function(result){
							updateDisplayedElements();
						});
					});
				})();
				$("#item-container").append(newElement);
			};
		}
	}
	
	function displayCategoriesList(){
		$("#category-container").empty();
		for(var i = 0; i < categories.length; i++){
				var newElement = categoryListElement.clone(true);
				newElement.find(".category-select-link").text(categories[i][1]);
				newElement.find(".category-select-link").attr("href", "#category=" + categories[i][1]);
				//Capture the index so the handler will have the value at this point in the loop, rather than when the handler fires.
				(function(){
					var index = i;
					newElement.find(".category-delete").data("target", categories[index][1]).click(function(){
						$.ajax("/categories/" + categories[index][0] + "/delete", 
						{
							method : "DELETE"
						}).fail(function(result){
							console.log(result);
							alert("Something went wrong trying to delete the category.");
						}).done(function(result){
							updateDisplayedElements();
						});
					});
					newElement.find(".update-form").attr("id", "update-category-" + index);
					newElement.find(".category-update").attr("data-target", "#update-category-" + index);
					newElement.find(".update-category-name").attr("id", "update-category-name-" + index);
					var updateButton = newElement.find(".update-category-name-button");
					newElement.find(".update-category-name-button").click(function(event){
						$.ajax("categories/" + categories[index][1] +"/update", {
							method : "PUT",
							data : JSON.stringify({
								category : {
									id : categories[index][0],
									description : $("#update-category-name-"+index).val()
								}
							}),
							contentType : "application/json; charset=utf-8",
							headers : {
								"user_id_token" : user.Zi.id_token
							}
						}).fail(function(){
							alert("Something went wrong while trying to update the category.");
						}).done(function(){
							updateDisplayedElements();
						})
					})
				})();
				$("#category-container").append(newElement);
				var option = $("<option>", {
					value : categories[i][0],
					text : categories[i][1]
				});
				$("#new-item-category").append(option);
			};
	}
	
	function displayItemDescription(){
		//Only update if there is a selected item and it has changed.
		if(selectedItem){
			if(selectedItem !== previousItem){
				$(".update-item").show(100);
				$("#item-description").text(items.find(function(e){
					return e[0] == selectedItem;
				})[2]);
				$("#item-name").text(items.find(function(e){
					return e[0] == selectedItem;
				})[1]);
				$("#update-item-button").attr("data-id", selectedItem);
				}
		} else {
			$("#item-name").text("No item to display.");
			$("#item-description").text("");
			$(".update-item").hide(100);
		};
	};
	
	//Update the display
	function updateDisplayedElements(){
		updateSelected().then(function(){
			displayItemsList();
			displayCategoriesList();
			displayItemDescription();
		});
	};
	
	//Item and category selection are determined by the url hash
	$(window).on('hashchange', function(event){
		updateDisplayedElements();
	});
	
	$("#new-category-submit").click(function(event){
		var newCategory = $("#category-name").val();
		$.ajax("/categories/create",
		{
			method : "POST",
			data : JSON.stringify({
				category : newCategory
			}),
			contentType: 'application/json; charset=utf-8',
			headers : {
				"user_id_token" : user.Zi.id_token
			}
		}).fail(function(result){
			console.log(result);
			alert("Oops, something went wrong.");
		}).done(function(){
			updateDisplayedElements();
		});
	});
	
	$("#new-item-submit").click(function(event){
		var itemName = $("#new-item-name").val();
		var itemDescription = $("#new-item-description").val();
		var itemCategory = $("#new-item-category").val();
		
		$.ajax("/items/create",
		{
			method : "POST",
			data : JSON.stringify({
				item : {
					name : itemName,
					description : itemDescription,
					category : itemCategory
				}
			}),
			contentType: 'application/json; charset=utf-8',
			headers : {
				"user_id_token" : user.Zi.id_token
			}
		}).fail(function(result){
			console.log(result);
			alert("Oops, something went wrong.");
		}).done(function(){
			updateDisplayedElements();
		});
	});
	
	$("#update-item-button").click(function(event){
		var itemName = $("#update-item-name").val();
		var itemDescription = $("#new-item-description").val();
		var itemId = $("#update-item-button").data("id");
		
		$.ajax("/items/"+ selectedItem +"/update",
		{
			method : "PUT",
			data : JSON.stringify({
				item : {
					name : itemName ? itemName : null,
					description : itemDescription ? itemDescription : null,
					id : itemId
				}
			}),
			contentType: 'application/json; charset=utf-8',
			dataType : "json",
			headers : {
				"user_id_token" : user.Zi.id_token
			}
		}).fail(function(result){
			console.log(result);
			alert("Oops, something went wrong.");
		}).done(function(){
			if(itemName){
				window.location.hash = "item=" + itemName
			}
			//Force the item display to update
			selectedItem = undefined;
			updateDisplayedElements();
		});
	});
	
	$("#new-item").click(function(event){
		var target = $(event.target);
		if(target.attr("aria-expanded")){
			target.text("Add Category");
		} else {
			target.text("Nevermind");
		}
	});	
	updateDisplayedElements();
});

function signOut(){
	var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
      console.log('User signed out.');
    });
};

function onSignIn(googleUser){
	$.ajax("/login", {
		method : "POST",
		data : JSON.stringify({
			"idToken" : googleUser.getAuthResponse().id_token
		}),
		contentType : "application/json; charset=utf-8"
	}).fail(function(response){
		console.log("The server failed to validate the login.");
		console.log(response.responseText);
	});
};